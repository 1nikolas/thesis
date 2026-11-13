from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional
import ast

ResponseType = TypeVar('ResponseType')

class BaseResponse(Generic[ResponseType], ABC):
    @abstractmethod
    def parse(self, response: str) -> Optional[ResponseType]:
        pass


class StringResponse(BaseResponse[str]):
    def parse(self, response: str) -> Optional[str]:
        return response


class NumberResponse(BaseResponse[int]):
    def parse(self, response: str) -> Optional[int]:
        return int(response) if response.isdigit() else None


class ListResponse(BaseResponse[list]):
    def parse(self, response: str) -> Optional[list]:
        try:
            parsed = ast.literal_eval(response)
            if isinstance(parsed, list):
                return parsed
            return None
        except (ValueError, SyntaxError):
            return None


class LiteralResponse(BaseResponse[str]):
    def __init__(self, literal_values: list[str]):
        self.literal_values: list[str] = literal_values

    def parse(self, response: str) -> Optional[str]:
        response_parsed = response.lower().strip()

        if response_parsed in self.literal_values:
            return response_parsed
        return None


class CoTStringResponse(BaseResponse[str]):
    def __init__(self, marker: str):
        self.marker = marker.lower().rstrip(":")

    def parse(self, response: str) -> Optional[str]:
        index = response.lower().rfind(self.marker + ":")

        if index == -1:
            index = response.lower().rfind(self.marker + "**:")

            if index == -1:
                return None

            return response[index + len(self.marker) + 3:].strip()


        return response[index + len(self.marker) + 1:].strip()