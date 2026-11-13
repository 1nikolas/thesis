import os
import traceback

from openai import OpenAI

from ..base_client import BaseClient
from .responses import BaseResponse, ResponseType

LLM_RETRIES = 3


class LLMClient(BaseClient):
    def __init__(self, model: str):
        self.model = model

        self.client = OpenAI(base_url="https://api.featherless.ai/v1", api_key=os.environ["FEATHERLESS_TOKEN"])

    def close(self):
        self.client.close()

    @staticmethod
    def get_caller_class():
        import inspect

        for frame_info in inspect.stack()[2:]:
            if 'self' in frame_info.frame.f_locals:
                return frame_info.frame.f_locals['self'].__class__.__name__
        return "Unknown"

    def ask(self, system_prompt: str, user_prompt: str,
            response_parser: BaseResponse[ResponseType], stop=None) -> ResponseType | None:
        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt,
            }
        ]

        return self.ask_raw(messages, response_parser, stop)

    def ask_raw(self, messages: list, response_parser: BaseResponse[ResponseType], stop: list | None = None) -> ResponseType | None:
        for i in range(LLM_RETRIES):
            try:
                response = self.__get_llm_response(messages, stop)
            except (Exception,):
                print(traceback.format_exc())
                continue

            print(f"{LLMClient.get_caller_class()} LLM Response: {response}")

            response_parsed = response_parser.parse(response)

            if response_parsed is not None:
                return response_parsed

        return None

    def __get_llm_response(self, messages: list, stop: list | None) -> str:
        if stop is None:
            stop = []

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stop=stop,
            stream=False,
            extra_body={'chat_template_kwargs': {'enable_thinking': False}}
        )

        # noinspection unresolved-references
        return response.choices[0].message.content.replace("\\n", "\n").replace("`", "")
