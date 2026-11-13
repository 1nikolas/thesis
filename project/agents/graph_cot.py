import json
from typing import Type
import re

from agentlib import Agent, Step, StepOutput
from agentlib.clients import LLMClient, Neo4jClient, BaseClient
from agentlib.clients.llm import LiteralResponse, StringResponse
from agentlib.step import StepOutputStatus

from agents.prompts import SCHEMA, GUARDRAILS_SYSTEM, GUARDRAILS_USER, GRAPH_COT_REASON_SYSTEM, GRAPH_COT_REASON_USER, \
    GRAPH_COT_GEN_ANSWER_SYSTEM, GRAPH_COT_GEN_ANSWER_USER
from utils import GraphCotTools

ACTION_RE = re.compile(r"Action\s*\d*\s*:\s*(\w+)\s*\[(.*)]")

MAX_STEPS = 50


class GraphCoTAgent(Agent):
    class GuardrailsStep(Step):
        def process(self) -> StepOutput:
            llm_client: LLMClient = self.get_client(LLMClient)
            question: str = self.input_data["question"]
            full_schema: dict = self.input_data["full_schema"]

            llm_response = llm_client.ask(
                GUARDRAILS_SYSTEM,
                GUARDRAILS_USER(question, SCHEMA(full_schema['nodes'],
                                                 full_schema['relations'],
                                                 full_schema['simple_connections'])),
                LiteralResponse(["yes", "no"]),
            )

            if llm_response is None:
                return StepOutput(StepOutputStatus.LLM_FAILED)

            if llm_response == "yes":
                return StepOutput(StepOutputStatus.SUCCESS, GraphCoTAgent.ReasonStep,
                                  {"question": question, "scratchpad": [], "step_count": 0,
                                   "full_schema": full_schema})

            if llm_response == "no":
                return StepOutput(StepOutputStatus.GUARDRAILS_FAILED)

            return StepOutput(StepOutputStatus.LLM_FAILED)

    class ReasonStep(Step):
        def process(self) -> StepOutput:
            llm_client: LLMClient = self.get_client(LLMClient)

            question: str = self.input_data["question"]
            scratchpad: list[tuple] = self.input_data["scratchpad"]
            step_count: int = self.input_data["step_count"]
            full_schema: dict = self.input_data["full_schema"]

            if step_count >= MAX_STEPS:
                return StepOutput(StepOutputStatus.STEPS_EXHAUSTED, None,
                                  {"question": question, "scratchpad": scratchpad})

            messages = [{"role": "system", "content": GRAPH_COT_REASON_SYSTEM},
                        {"role": "user", "content": GRAPH_COT_REASON_USER(
                            SCHEMA(full_schema['nodes'], full_schema['relations'], full_schema['simple_connections']),
                            question)}]

            for reason_action, observation in scratchpad:
                messages.append({"role": "assistant", "content": reason_action})
                messages.append({"role": "user", "content": observation})

            reason_action_text = llm_client.ask_raw(messages, StringResponse(), ["Observation:", "\nObservation"])

            if reason_action_text is None:
                return StepOutput(StepOutputStatus.LLM_FAILED)

            reason_action_text = reason_action_text.strip()
            match = ACTION_RE.search(reason_action_text)

            if match is None:
                scratchpad.append((reason_action_text,
                                   "Observation: Invalid format. Reply with one line 'Action: FunctionName[args]'"))
                return StepOutput(StepOutputStatus.SUCCESS, GraphCoTAgent.ReasonStep,
                                  {"question": question, "scratchpad": scratchpad, "step_count": step_count + 1,
                                   "full_schema": full_schema})

            action_name = match.group(1).strip()
            action_args = match.group(2).strip()

            if action_name.lower() == "finish":
                try:
                    action_args = json.loads(f"[{action_args}]")
                except json.JSONDecodeError:
                    scratchpad.append((reason_action_text,
                                       "Observation: Finish function argument invalid. Reply with one line 'Action: Finish[JSON list of rows]'"))

                    return StepOutput(StepOutputStatus.SUCCESS, GraphCoTAgent.ReasonStep,
                                      {"question": question, "scratchpad": scratchpad, "step_count": step_count + 1,
                                       "full_schema": full_schema})

                scratchpad.append((reason_action_text, ""))

                return StepOutput(StepOutputStatus.SUCCESS, GraphCoTAgent.GenAnswerStep,
                                  {"question": question, "scratchpad": scratchpad, "query_ans": action_args})

            return StepOutput(StepOutputStatus.SUCCESS, GraphCoTAgent.ExecuteStep,
                              {"question": question, "scratchpad": scratchpad, "step_count": step_count,
                               "reason_action_text": reason_action_text, "action_name": action_name,
                               "action_args": action_args, "full_schema": full_schema})

    class ExecuteStep(Step):
        def process(self) -> StepOutput:
            neo4j_client: Neo4jClient = self.get_client(Neo4jClient)

            question: str = self.input_data["question"]
            scratchpad: list[tuple] = self.input_data["scratchpad"]
            step_count: int = self.input_data["step_count"]
            reason_action_text: str = self.input_data["reason_action_text"]
            action_name: str = self.input_data["action_name"]
            action_args: str = self.input_data["action_args"]
            full_schema: dict = self.input_data["full_schema"]

            tools = GraphCotTools(neo4j_client)
            observation = tools.run(action_name, action_args.replace('"', '').replace("'", ''))

            scratchpad.append((reason_action_text, f"Observation: {observation}"))

            return StepOutput(StepOutputStatus.SUCCESS, GraphCoTAgent.ReasonStep,
                              {"question": question, "scratchpad": scratchpad, "step_count": step_count + 1,
                               "full_schema": full_schema})

    class GenAnswerStep(Step):
        def process(self) -> StepOutput:
            llm_client: LLMClient = self.get_client(LLMClient)

            question: str = self.input_data["question"]
            scratchpad: list[tuple] = self.input_data["scratchpad"]

            llm_response = llm_client.ask(
                GRAPH_COT_GEN_ANSWER_SYSTEM,
                GRAPH_COT_GEN_ANSWER_USER(scratchpad, question),
                StringResponse(),
            )

            if llm_response is None:
                return StepOutput(StepOutputStatus.LLM_FAILED)

            return StepOutput(StepOutputStatus.SUCCESS, None, {"answer": llm_response})

    def _get_required_clients(self) -> list[type[BaseClient]]:
        return [Neo4jClient, LLMClient]

    def _get_init_step(self) -> Type[Agent.StepType]:
        return GraphCoTAgent.GuardrailsStep
