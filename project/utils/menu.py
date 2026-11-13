import os
from typing import Callable


def ask_str(question: str, check: Callable[[str], bool]) -> str:
    print(question)

    answer = ''

    while not check(answer):
        answer = input("Input> ")

    print()

    return answer


def ask_int(question: str, check: Callable[[int], bool]) -> int:
    print(question)

    answer = ''

    while not answer.isdigit() or not check(int(answer)):
        answer = input("Input> ")

    print()

    return int(answer)


def ask_choice(question: str, choices: list) -> int:
    print(question)

    for i in range(len(choices)):
        choice = choices[i]

        if isinstance(choice, type):
            choice = choice.__name__

        print(f"\t{i + 1}) {choice}")

    answer = ''
    while not answer.isdigit() or int(answer) < 1 or int(answer) > len(choices):
        answer = input("Choice> ")

    print()

    return int(answer) - 1


def ask_yes_no(question: str) -> bool:
    print(question)

    answer = ''
    while answer not in ['y', 'n']:
        answer = input("Choice (y/n)> ")

    print()

    return answer == 'y'


def ask_result_files(dataset: str, models: list[str], four_files: bool = False) -> tuple[str, str] | tuple[
    str, str, str, str]:
    def get_two_files(cmp=False) -> tuple[str, str]:
        mdl = models[ask_choice("Choose a model", models)]

        base_path = f"../data/{dataset}/{mdl.replace("/", ".")}/"
        if not os.path.isdir(base_path):
            print("No result files found")
            exit(0)

        files = [f for f in os.listdir(base_path) if f.endswith("_results.json")]
        files.sort()

        if len(files) < 2:
            print("Not enough result files found")
            exit(0)

        file1_idx = ask_choice(f"Choose first{" comparing" if cmp else ""} results file", files)
        file1 = base_path + files[file1_idx]

        file2_idx = ask_choice(f"Choose second{" comparing" if cmp else ""} results file", files)
        file2 = base_path + files[file2_idx]

        return file1, file2

    return get_two_files() + get_two_files(True) if four_files else get_two_files()
