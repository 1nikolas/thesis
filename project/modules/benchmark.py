import json
import os
import random
import threading
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
from typing import Callable

from agentlib import StepOutput
from agentlib.clients import LLMClient, Neo4jClient
from agentlib.step import StepOutputStatus
from utils import normalize_records, is_answer_correct
from utils import RunConfig
from utils import get_dataset_creds


class BenchmarkResult(Enum):
    UNKNOWN = -1
    CORRECT = 0  # guardrails blocked unanswerable question or answer was correct
    INCORRECT = 1  # answer incorrect
    GUARDRAILS_FALSE_POSITIVE = 2  # got an answer but question unanswerable
    GUARDRAILS_FALSE_NEGATIVE = 3  # guardrail blocked but question answerable
    LLM_FAILED = 4  # LLM gave unexpected answer
    CYPHER_FAILED = 5  # Cypher did not run / syntax error (only applicable for non retry agnets)
    RETRY_EXHAUSTED = 6  # 3 Retries reached and still errors out (CYPHER_FAILED)
    STEPS_EXHAUSTED = 7  # GraphCoT MAX_STEPS steps reached


class Stats:
    def __init__(self, run_conf: RunConfig):
        self.run_conf = run_conf

        self.total = 0
        self.per_result: dict[BenchmarkResult, int] = {}
        self.raw_results: list[dict] = []


class Benchmark:
    def __init__(self, run_conf: RunConfig, dataset: str, model: str, questions: list[dict], full_schema: dict,
                 rules: dict, benchmark_done: Callable[[Stats], None]):
        self.run_conf = run_conf
        self.dataset = dataset
        self.model = model
        self.benchmark_done = benchmark_done

        self.questions = list(questions)
        random.shuffle(self.questions)
        self.full_schema = full_schema
        self.rules = rules

        self.q_count = len(self.questions)

        self.stats = Stats(run_conf)

        self.__lock = threading.Lock()

        self.__start()

    @staticmethod
    def to_int(s, default):
        try:
            return int(s)
        except (ValueError, TypeError):
            return default

    def __start(self):
        with ThreadPoolExecutor(max_workers=Benchmark.to_int(os.environ["BENCH_MAX_THREADS"], 1)) as pool:
            for i in range(self.q_count):
                pool.submit(self.__run_question, self.questions[i])

        self.stats.per_result = dict(sorted(self.stats.per_result.items(), key=lambda x: x[1], reverse=True))
        self.benchmark_done(self.stats)

    def __run_question(self, qa: dict):
        print(f"QUESTION: {qa['question']}")

        self.run_conf.agent({"question": qa['question'], 'full_schema': self.full_schema, "rules": self.rules,
                             "options": self.run_conf.options},
                            {LLMClient: {"model": self.model}, Neo4jClient: {"creds": get_dataset_creds(self.dataset)}},
                            lambda out: self.__on_done(qa, out), "GenAnswerStep")

        print("\n\n================================================================\n\n")

    @staticmethod
    def __get_benchmark_result(qa: dict, out: StepOutput) -> BenchmarkResult:
        status = out.status

        if status == StepOutputStatus.GUARDRAILS_FAILED:
            if not qa['answerable']:
                return BenchmarkResult.CORRECT
            return BenchmarkResult.GUARDRAILS_FALSE_NEGATIVE

        if status in (StepOutputStatus.SUCCESS, StepOutputStatus.CYPHER_FAILED, StepOutputStatus.RETRY_EXHAUSTED,
                      StepOutputStatus.STEPS_EXHAUSTED):
            if not qa['answerable']:
                return BenchmarkResult.GUARDRAILS_FALSE_POSITIVE

        if status == StepOutputStatus.SUCCESS:
            if is_answer_correct(out.out_data['query_ans'], qa['answers']):
                return BenchmarkResult.CORRECT
            else:
                return BenchmarkResult.INCORRECT

        if status == StepOutputStatus.LLM_FAILED:
            return BenchmarkResult.LLM_FAILED

        if status == StepOutputStatus.CYPHER_FAILED:
            return BenchmarkResult.CYPHER_FAILED

        if status == StepOutputStatus.RETRY_EXHAUSTED:
            return BenchmarkResult.RETRY_EXHAUSTED

        if status == StepOutputStatus.STEPS_EXHAUSTED:
            return BenchmarkResult.STEPS_EXHAUSTED

        return BenchmarkResult.UNKNOWN

    def __record_result(self, qa: dict, bench_res: BenchmarkResult, out: StepOutput):
        result = {"qid": qa['qid'], "template": qa["template"], "question": qa['question'], "result": bench_res}

        if bench_res == BenchmarkResult.INCORRECT:
            if 'query' in out.out_data:
                result['query'] = out.out_data['query']

            if 'scratchpad' in out.out_data:
                result['scratchpad'] = out.out_data['scratchpad']

            result['query_ans'] = normalize_records([r.data() for r in out.out_data['query_ans']]) \
                if len(out.out_data['query_ans']) > 0 and hasattr(out.out_data['query_ans'][0], 'data') \
                else out.out_data['query_ans']

            result['answers'] = qa['answers']

        if bench_res == BenchmarkResult.CYPHER_FAILED:
            result['query'] = out.out_data['query']
            result['errors'] = out.out_data['errors']

        if bench_res == BenchmarkResult.STEPS_EXHAUSTED:
            if 'scratchpad' in out.out_data:
                result['scratchpad'] = out.out_data['scratchpad']

        self.stats.raw_results.append(result)

    def __on_done(self, qa: dict, out: StepOutput):
        bench_res = self.__get_benchmark_result(qa, out)

        with self.__lock:
            self.__record_result(qa, bench_res, out)

            print(f"\n\nResult: {bench_res}")
            print(f"{self.q_count - self.stats.total - 1} questions left")

            if bench_res not in self.stats.per_result:
                self.stats.per_result[bench_res] = 0

            self.stats.per_result[bench_res] += 1

            self.stats.total += 1


class Benchmarker:
    def __init__(self, run_configs: list[RunConfig], dataset: str, model: str):
        self.run_configs = run_configs
        self.dataset = dataset
        self.model = model

        self.agent_stats: list[Stats] = []

        with open(f"../data/{self.dataset}/schema.json") as f:
            self.full_schema = json.load(f)

        with open(f"../data/{self.dataset}/questions.json") as f:
            self.questions = json.load(f)

        self.rules = {}

        if self.__needs_rules(run_configs):
            with open(f"../data/{self.dataset}/{self.model.replace("/", ".")}/rules.json") as f:
                self.rules = json.load(f)

        self.__run()

    @staticmethod
    def __needs_rules(run_configs: list[RunConfig]) -> bool:
        for run_config in run_configs:
            if "rules" in run_config.options:
                return True
        return False

    def __run(self):
        if not self.run_configs:
            agent_count = {}
            for stats in self.agent_stats:
                agent_name = stats.run_conf.agent.__name__
                agent_count[agent_name] = 1 if agent_name not in agent_count else agent_count[agent_name] + 1

                print(f"{agent_name} Run {agent_count[agent_name]} Stats:")

                for (status, count) in stats.per_result.items():
                    status_percent = (count / stats.total) * 100
                    print(f"\t{status}: {status_percent:.2f}% ({count} / {stats.total})")

                print()

                options_str = "".join(f"_{opt}_{val}" for opt, val in stats.run_conf.options.items())

                with open(
                        f"../data/{self.dataset}/{self.model.replace("/", ".")}/{agent_name}{options_str}_run_{agent_count[agent_name]}_results.json",
                        "w") as of:
                    of.write(json.dumps(stats.raw_results, default=str))

            return

        run_conf = self.run_configs.pop(0)
        Benchmark(run_conf, self.dataset, self.model, self.questions, self.full_schema, self.rules, self.__on_done)

    def __on_done(self, stats: Stats):
        self.agent_stats.append(stats)
        self.__run()
