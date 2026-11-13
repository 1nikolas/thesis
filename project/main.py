import os
from typing import Any

from agents import CypherGenV1Agent, CypherGenV2Agent, CypherGenV3Agent, CypherGenV4Agent, CypherGenV5Agent, \
    GraphCoTAgent
from modules import SimpleQuestion, Benchmarker, GenerateRules, AnalyzeResults, BuildSchema, GenerateQuestions
from utils import RunConfig, ask_str, ask_choice, ask_yes_no, ask_result_files

ENVS = ["BENCH_MAX_THREADS", "FEATHERLESS_TOKEN", "NEO_FTTH_URI", "NEO_FTTH_USER", "NEO_FTTH_PASS", "NEO_HOSPITAL_URI",
        "NEO_HOSPITAL_USER", "NEO_HOSPITAL_PASS", "NEO_ECOM_URI", "NEO_ECOM_USER", "NEO_ECOM_PASS"]

DATASETS = ['ftth', 'hospital', 'ecommerce']

USABLE_AGENTS: list[dict[str, Any]] = [
    dict(agent=CypherGenV1Agent, options={}),
    dict(agent=CypherGenV2Agent, options={}),
    dict(agent=CypherGenV3Agent, options={"rules": ["auto", "human"]}),
    dict(agent=CypherGenV4Agent, options={"rules": ["auto", "human"]}),
    dict(agent=CypherGenV5Agent, options={"rules": ["auto", "human"]}),
    dict(agent=GraphCoTAgent, options={}),
]

MODELS = ["meta-llama/Llama-3.3-70B-Instruct", "neo4j/text-to-cypher-Gemma-3-27B-Instruct-2025.04.0",
          "Qwen/Qwen3-Coder-Next", "Qwen/Qwen3.8-27B"]


def benchmark():
    dataset_idx = ask_choice("Choose a dataset", DATASETS)
    model_idx = ask_choice("Choose a model", MODELS)

    agents_list = [entry["agent"] for entry in USABLE_AGENTS]
    run_configs: list[RunConfig] = []

    while True:
        agent_idx = ask_choice("Choose an agent", agents_list)
        agent_opt = USABLE_AGENTS[agent_idx]["options"]

        options = {}

        for opt, values in agent_opt.items():
            opt_idx = ask_choice(f"Choose an option for {opt}", values)
            options[opt] = values[opt_idx]

        run_configs.append(RunConfig(USABLE_AGENTS[agent_idx]["agent"], options))

        if not ask_yes_no("More?"):
            break

    Benchmarker(run_configs, DATASETS[dataset_idx], MODELS[model_idx])


def generate_rules():
    dataset_idx = ask_choice("Choose a dataset", DATASETS)
    model_idx = ask_choice("Choose a model", MODELS)

    dataset = DATASETS[dataset_idx]
    model = MODELS[model_idx]

    file1, file2 = ask_result_files(dataset, MODELS)

    GenerateRules(file1, file2, DATASETS[dataset_idx], model)


def simple_question():
    dataset_idx = ask_choice("Choose a dataset", DATASETS)
    model_idx = ask_choice("Choose a model", MODELS)

    agent_idx = ask_choice("Choose an agent", [entry["agent"] for entry in USABLE_AGENTS])
    agent_opt = USABLE_AGENTS[agent_idx]["options"]

    options = {}

    for opt, values in agent_opt.items():
        opt_idx = ask_choice(f"Choose an option for {opt}", values)
        options[opt] = values[opt_idx]

    question = ''

    while not question:
        question = input("Question> ")

    print()

    SimpleQuestion(RunConfig(USABLE_AGENTS[agent_idx]["agent"], options), question, DATASETS[dataset_idx],
                   MODELS[model_idx])


def build_schema():
    dataset_idx = ask_choice("Choose a dataset", DATASETS)

    BuildSchema(DATASETS[dataset_idx])


def question_gen():
    dataset_idx = ask_choice("Choose a dataset", DATASETS)

    GenerateQuestions(DATASETS[dataset_idx])


def analyze_results():
    dataset_idx = ask_choice("Choose a dataset", DATASETS)

    dataset = DATASETS[dataset_idx]

    mode = ask_choice("Choose mode", ["Total Results", "Results Per Template", "Per Template % Points Difference"])

    files = ask_result_files(dataset, MODELS, mode == 2)

    exclude: list[int] = []
    if ask_yes_no("Exclude Templates?"):
        ans = ask_str("Enter Template IDs comma separated", lambda x: all(i.isdigit() for i in x.split(",")))
        exclude = [int(i) for i in ans.split(",")]

    pretty_print = ask_yes_no("Pretty print?")

    AnalyzeResults(mode, files, exclude, pretty_print)


def check_envs() -> None:
    for var in ENVS:
        if var not in os.environ:
            raise Exception(f"Env {var} is not set")


def main():
    check_envs()

    module = ask_choice("What to run?", ["Run the Benchmark Module", "Run the Automatic Rule Generation Module",
                                         "Run a Simple Question", "Run the Database Schema Extraction",
                                         "Run the Dataset Question Generation", "Run the Benchmark Result Analysis"])

    match module:
        case 0:
            benchmark()
        case 1:
            generate_rules()
        case 2:
            simple_question()
        case 3:
            build_schema()
        case 4:
            question_gen()
        case 5:
            analyze_results()


if __name__ == "__main__":
    main()
