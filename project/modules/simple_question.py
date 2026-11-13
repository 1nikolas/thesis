import json

from agentlib import StepOutput
from agentlib.clients import LLMClient, Neo4jClient
from utils import get_dataset_creds
from utils import RunConfig


class SimpleQuestion:
    def __init__(self, run_conf: RunConfig, question: str, dataset: str, model: str):
        self.run_conf = run_conf

        self.question = question

        with open(f"../data/{dataset}/schema.json") as f:
            full_schema = json.load(f)

        rules = {}

        if "rules" in run_conf.options:
            with open(f"../data/{dataset}/{model.replace("/", ".")}/rules.json") as f:
                rules = json.load(f)

        self.run_conf.agent(
            {"question": self.question, 'full_schema': full_schema, "rules": rules, "options": run_conf.options},
            {LLMClient: {"model": model}, Neo4jClient: {"creds": get_dataset_creds(dataset)}}, self.__on_done)

    @staticmethod
    def __on_done(out: StepOutput):
        print()
        print(f"Status: {out.status}")
        print(f"Output: {out.out_data}")
