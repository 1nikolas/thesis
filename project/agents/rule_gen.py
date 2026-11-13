from typing import Type

from agentlib import Agent, Step, StepOutput
from agentlib.clients import BaseClient, LLMClient
from agentlib.clients.llm.responses import CoTStringResponse
from agentlib.step import StepOutputStatus
from agents.prompts import RULE_GEN_SYSTEM, SCHEMA, RULE_GEN_USER


class RuleGenAgent(Agent):
    class RuleGenStep(Step):
        def process(self) -> StepOutput:
            llm_client: LLMClient = self.get_client(LLMClient)

            question: str = self.input_data["question"]
            cypher: str = self.input_data["cypher"]
            golden_cypher: str = self.input_data["golden_cypher"]
            full_schema: dict = self.input_data["full_schema"]

            llm_response = llm_client.ask(RULE_GEN_SYSTEM, RULE_GEN_USER(cypher, golden_cypher,
                                                                         SCHEMA(full_schema['nodes'],
                                                                                full_schema['relations'],
                                                                                full_schema['connections']), question),
                                          CoTStringResponse("rule"))

            if llm_response is None:
                return StepOutput(StepOutputStatus.LLM_FAILED)

            return StepOutput(StepOutputStatus.SUCCESS, None, {"rule": llm_response})

    def _get_required_clients(self) -> list[type[BaseClient]]:
        return [LLMClient]

    def _get_init_step(self) -> Type[Agent.StepType]:
        return RuleGenAgent.RuleGenStep
