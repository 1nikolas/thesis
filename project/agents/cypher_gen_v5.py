from typing import Type

from neo4j.exceptions import Neo4jError

from agentlib import Agent, StepOutput, Step
from agentlib.clients import BaseClient, Neo4jClient, LLMClient
from agentlib.clients.llm import LiteralResponse, StringResponse
from agentlib.clients.llm.responses import CoTStringResponse
from agentlib.step import StepOutputStatus
from agents.prompts import GUARDRAILS_SYSTEM, GUARDRAILS_USER, SCHEMA, GEN_QUERY_USER, GEN_ANSWER_SYSTEM, \
    GEN_ANSWER_USER, RETRY_QUERY_USER, GEN_QUERY_SYSTEM_COT, RETRY_QUERY_SYSTEM_COT
from utils import CypherQueryCorrector


class CypherGenV5Agent(Agent):
    class GuardrailsStep(Step):
        def process(self) -> StepOutput:
            llm_client: LLMClient = self.get_client(LLMClient)
            question: str = self.input_data["question"]
            full_schema: dict = self.input_data["full_schema"]
            rules_dict: dict = self.input_data["rules"]
            options: dict = self.input_data["options"]

            llm_response = llm_client.ask(GUARDRAILS_SYSTEM,
                                          GUARDRAILS_USER(question, SCHEMA(full_schema['nodes'],
                                                                           full_schema['relations'],
                                                                           full_schema['connections'])),
                                          LiteralResponse(["yes", "no"]))

            if llm_response is None:
                return StepOutput(StepOutputStatus.LLM_FAILED)

            if llm_response == "yes":
                return StepOutput(StepOutputStatus.SUCCESS, CypherGenV5Agent.GenQueryStep,
                                  {"question": question, "full_schema": full_schema, "rules_dict": rules_dict,
                                   "options": options})

            if llm_response == "no":
                return StepOutput(StepOutputStatus.GUARDRAILS_FAILED)

            return StepOutput(StepOutputStatus.LLM_FAILED)

    class GenQueryStep(Step):
        def process(self) -> StepOutput:
            llm_client: LLMClient = self.get_client(LLMClient)

            question: str = self.input_data["question"]
            full_schema: dict = self.input_data["full_schema"]
            rules_dict: dict = self.input_data["rules_dict"]
            options: dict = self.input_data["options"]

            if "rules" in options and options["rules"] in ("auto", "human"):
                rules: str = rules_dict["rules"] if options["rules"] == "auto" else rules_dict["rules_human"]
            else:
                raise Exception("Rules Error!")


            llm_response = llm_client.ask(GEN_QUERY_SYSTEM_COT, GEN_QUERY_USER(rules, SCHEMA(full_schema['nodes'],
                                                                                         full_schema['relations'],
                                                                                         full_schema['connections']),
                                                                           question), CoTStringResponse("cypher"))

            if llm_response is None:
                return StepOutput(StepOutputStatus.LLM_FAILED)

            return StepOutput(StepOutputStatus.SUCCESS, CypherGenV5Agent.CorrectQueryStep,
                              {"query": llm_response, "question": question, "full_schema": full_schema})

    class RetryQueryStep(Step):
        def process(self) -> StepOutput:
            llm_client: LLMClient = self.get_client(LLMClient)

            question: str = self.input_data["question"]
            errors: list[str] = self.input_data["errors"]
            error_query: str = self.input_data["error_query"]
            full_schema: dict = self.input_data["full_schema"]
            retry_count: int = self.input_data["retry_count"]

            if retry_count == 3:
                return StepOutput(StepOutputStatus.RETRY_EXHAUSTED)

            retry_count += 1

            llm_response = llm_client.ask(RETRY_QUERY_SYSTEM_COT, RETRY_QUERY_USER(question, error_query, errors,
                                                                               SCHEMA(full_schema['nodes'],
                                                                                      full_schema['relations'],
                                                                                      full_schema['connections'])),
                                          CoTStringResponse("cypher"))

            if llm_response is None:
                return StepOutput(StepOutputStatus.LLM_FAILED)

            return StepOutput(StepOutputStatus.SUCCESS, CypherGenV5Agent.CorrectQueryStep,
                              {"query": llm_response, "question": question, "full_schema": full_schema,
                               "retry_count": retry_count})

    class CorrectQueryStep(Step):
        def process(self) -> StepOutput:
            question: str = self.input_data["question"]
            query: str = self.input_data["query"]
            full_schema: dict = self.input_data["full_schema"]
            retry_count: int = self.input_data["retry_count"] if "retry_count" in self.input_data else 0

            corrector = CypherQueryCorrector(full_schema['schema'])
            corrector_res = corrector(query)

            if corrector_res.has_error:
                return StepOutput(StepOutputStatus.SUCCESS, CypherGenV5Agent.RetryQueryStep,
                                  {"question": question, "error_query": query, "errors": [corrector_res.res],
                                   "full_schema": full_schema, "retry_count": retry_count})

            corrected_query = corrector_res.res

            print(f"Corrected: {corrected_query}")

            return StepOutput(StepOutputStatus.SUCCESS, CypherGenV5Agent.RunQueryStep,
                              {"query": corrected_query, "question": question, "full_schema": full_schema,
                               "retry_count": retry_count})

    class RunQueryStep(Step):
        def process(self) -> StepOutput:
            question: str = self.input_data["question"]
            query: str = self.input_data["query"]
            full_schema: dict = self.input_data["full_schema"]
            retry_count: int = self.input_data["retry_count"]

            neo4j_client: Neo4jClient = self.get_client(Neo4jClient)

            try:
                query_ans = neo4j_client.query(query)
            except Neo4jError as e:
                return StepOutput(StepOutputStatus.SUCCESS, CypherGenV5Agent.RetryQueryStep,
                                  {"question": question, "error_query": query, "errors": [e.message],
                                   "full_schema": full_schema, "retry_count": retry_count})

            if query_ans.warnings:
                return StepOutput(StepOutputStatus.SUCCESS, CypherGenV5Agent.RetryQueryStep,
                                  {"question": question, "error_query": query, "errors": query_ans.warnings,
                                   "full_schema": full_schema, "retry_count": retry_count})

            return StepOutput(StepOutputStatus.SUCCESS, CypherGenV5Agent.GenAnswerStep,
                              {"question": question, "query": query, "query_ans": query_ans.records})

    class GenAnswerStep(Step):
        def process(self) -> StepOutput:
            question: str = self.input_data["question"]
            query: str = self.input_data["query"]
            query_ans: list = self.input_data["query_ans"]

            llm_client: LLMClient = self.get_client(LLMClient)

            results = "The database returned no records." if len(query_ans) == 0 else "\n".join(
                str(result) for result in query_ans)

            llm_response = llm_client.ask(GEN_ANSWER_SYSTEM, GEN_ANSWER_USER(results, query, question),
                                          StringResponse())

            if llm_response is None:
                return StepOutput(StepOutputStatus.LLM_FAILED)

            return StepOutput(StepOutputStatus.SUCCESS, None, {"answer": llm_response})

    def _get_required_clients(self) -> list[type[BaseClient]]:
        return [Neo4jClient, LLMClient]

    def _get_init_step(self) -> Type[Agent.StepType]:
        return CypherGenV5Agent.GuardrailsStep
