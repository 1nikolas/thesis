from abc import ABC, abstractmethod
from enum import Enum
from typing import TypeVar
from .clients import BaseClient

ClientType = TypeVar('ClientType', bound=BaseClient)

class Step(ABC):
    def __init__(self, clients: dict[type[BaseClient], BaseClient], input_data: dict):
        self.clients: dict[type[BaseClient], BaseClient] = clients
        self.input_data: dict = input_data

    @abstractmethod
    def process(self) -> "StepOutput":
        pass

    def get_client(self, client: type[ClientType]) -> ClientType:
        assert client in self.clients
        assert isinstance(self.clients[client], client)
        return self.clients[client]


class StepOutput:
    def __init__(self, status: "StepOutputStatus", next_step: type[Step] | None = None, out_data: dict | None = None):
        self.status = status
        self.next_step = next_step
        self.out_data = {} if out_data is None else out_data

class StepOutputStatus(Enum):
    SUCCESS = 0
    GUARDRAILS_FAILED = 1
    LLM_FAILED = 2
    CYPHER_FAILED = 3
    RETRY_EXHAUSTED = 4
    STEPS_EXHAUSTED = 5

