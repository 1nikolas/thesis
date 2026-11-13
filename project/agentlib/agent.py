from abc import ABC, abstractmethod
from typing import Callable, TypeVar

from .step import Step, StepOutput
from .clients import BaseClient


class Agent(ABC):
    StepType = TypeVar('StepType', bound=Step)

    def __init__(self, input_data: dict, client_opt: dict[type[BaseClient], dict], end_function: Callable[[StepOutput], None], end_at: str | None = None):
        self.clients: dict[type[BaseClient], BaseClient] = {}

        for client in self._get_required_clients():
            options = client_opt.get(client, {})
            # noinspection argument-list
            self.clients[client] = client(**options)

        self.input_data = input_data
        self.end_function = end_function
        self.end_at = end_at

        self.__next_step(self._get_init_step(), input_data)

    @abstractmethod
    def _get_required_clients(self) -> list[type[BaseClient]]:
        """
        Example:
        return [Neo4jClient, LLMClient]
        """
        pass

    @abstractmethod
    def _get_init_step(self) -> type[StepType]:
        """
        Example:
        return MyStep
        """
        pass


    def __next_step(self, step: type[Step], input_data: dict):
        out: StepOutput = step(self.clients, input_data).process()

        print(f"{step.__name__} Output: {dict((k, v) for k, v in out.out_data.items() if k != "full_schema")}")


        if out.next_step is None or self.end_at == out.next_step.__name__:
            for client in self.clients.values():
                client.close()

            self.end_function(out)
            return

        self.__next_step(out.next_step, out.out_data)

