from typing import Type

from agentlib import Agent


class RunConfig:
    def __init__(self, agent: Type[Agent], options: dict):
        self.agent = agent
        self.options = options