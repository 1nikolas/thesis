import json
import random

from agentlib import StepOutput
from agentlib.clients import LLMClient, Neo4jClient
from agentlib.step import StepOutputStatus
from agents import CypherGenV3Agent, RuleGenAgent
from utils import is_answer_correct
from utils import get_dataset_creds


class GenerateRules:
    def __init__(self, file1: str, file2: str, dataset: str, model: str):
        self.dataset = dataset
        self.model = model

        self.questions: list[dict] = []
        self.rules: list[str] = []
        self.current_rule = ''
        self.current_run_outputs: list[StepOutput] = []
        self.questions_ok = 0

        with open(f"../data/{dataset}/schema.json") as f:
            self.full_schema = json.load(f)

        with open(f"../data/{dataset}/questions.json") as f:
            self.all_questions = json.load(f)

        qid_list = []


        with open(file1) as f:
            qid_list.extend(self.__parse_questions(json.load(f)))

        with open(file2) as f:
            qid_list.extend(self.__parse_questions(json.load(f)))

        qid_list = list(set(qid_list))

        for qid in qid_list:
            self.questions.append(self.__find_question(qid))

        self.__start()

    def __start(self):
        for question_dict in self.questions:
            for i in range(4):
                if self.__run(question_dict, i + 1):
                    break

            self.current_rule = ''

        print(self.__get_rules())
        print(f"Questions fixed: {self.questions_ok} / {len(self.questions)}")

    def __run(self, question_dict: dict, run: int) -> bool:
        self.current_run_outputs = []

        question = question_dict["question"]
        golden_cypher = question_dict["cypher"]
        answers = question_dict["answers"]

        for i in range(3):
            CypherGenV3Agent({"question": question, 'full_schema': self.full_schema, 'rules': {"rules": self.__get_rules()},
                     "options": {"rules": "auto"}},
                             {LLMClient: {"model": self.model}, Neo4jClient: {"creds": get_dataset_creds(self.dataset)}},
                             self.__record_result, "GenAnswerStep")
            print("\n\n================================================================\n\n")

        success_count = 0
        incorrect_cyphers: list[str] = []

        for out in self.current_run_outputs:
            if out.status == StepOutputStatus.SUCCESS:
                if is_answer_correct(out.out_data['query_ans'], answers):
                    success_count += 1
                else:
                    incorrect_cyphers.append(out.out_data['query'])
            if out.status == StepOutputStatus.CYPHER_FAILED:
                incorrect_cyphers.append(out.out_data['query'])

        if success_count >= 2:
            self.questions_ok += 1
            if self.current_rule:
                self.rules.append(self.current_rule)
            return True

        if run == 4 or len(incorrect_cyphers) == 0:
            return False

        cypher = random.choice(incorrect_cyphers)

        RuleGenAgent(
            {"question": question, 'cypher': cypher, 'golden_cypher': golden_cypher, 'full_schema': self.full_schema},
            {LLMClient: {"model": self.model}, Neo4jClient: {"creds": get_dataset_creds(self.dataset)}},
            self.__record_rule_result)
        print("\n\n================================================================\n\n")

        return False

    def __record_result(self, out: StepOutput):
        self.current_run_outputs.append(out)

    def __record_rule_result(self, out: StepOutput):
        self.current_rule = out.out_data["rule"]

    @staticmethod
    def __parse_questions(results) -> list:
        qids: list[int] = []

        for question in results:
            if question["result"] == "BenchmarkResult.INCORRECT" or question["result"] == "BenchmarkResult.CYPHER_FAILED":
                qids.append(question["qid"])

        return qids

    def __find_question(self, qid: int) -> dict:
        for question in self.all_questions:
            if question["qid"] == qid:
                return dict(question=question["question"], cypher=question["cypher"], answers=question["answers"])

        raise Exception(f"Qid not found in all questions")

    def __get_rules(self) -> str:
        rules_str = ""
        for rule in self.rules:
            rules_str += f"- {rule}\n"

        if self.current_rule:
            rules_str += f"- {self.current_rule}\n"

        return rules_str
