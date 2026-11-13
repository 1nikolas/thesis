import json
from collections import defaultdict
from enum import Enum


class ResultsMode(Enum):
    TOTAL_RESULTS = 0
    TEMPLATE_RESULTS = 1
    TEMPLATE_DIFF = 2


class Percent:
    def __init__(self, value: int | float, total: int = -1):
        if total == -1:
            self.percent = value
            return

        self.percent = (value / total) * 100

    def __repr__(self):
        return f"{self.percent:.2f}%"

    def __sub__(self, other):
        if not isinstance(other, Percent):
            return NotImplemented
        return Percent(self.percent - other.percent)


class AnalyzeResults:
    def __init__(self, mode: int, files: tuple[str, str] | tuple[str, str, str, str], exclude: list[int], pretty_print: bool):
        self.exclude = exclude
        self.pretty_print = pretty_print

        self.results: tuple = ()

        prev_len = -1
        for file in files:
            with open(file) as f:
                self.results += (json.load(f),)

            curr_len = sum(1 for i in self.results[-1] if i["template"] not in self.exclude)
            if prev_len != curr_len and prev_len != -1:
                print("Files don't have same number of results!")
                return
            prev_len = curr_len

        self.total = prev_len

        match ResultsMode(mode):
            case ResultsMode.TOTAL_RESULTS:
                self.total_results()
            case ResultsMode.TEMPLATE_RESULTS:
                self.template_results()
            case ResultsMode.TEMPLATE_DIFF:
                if len(self.results) != 4:
                    print("TEMPLATE_DIFF needs 4 results!")
                    return
                self.template_diff()

    def total_results(self):
        _stats: dict[str, list[int]] = defaultdict(lambda: [0, 0])

        results1, results2, *_ = self.results

        for results, idx in [(results1, 0), (results2, 1)]:
            for res in results:
                if res["template"] not in self.exclude:
                    _stats[res["result"]][idx] += 1

        stats = {k: (int(r1), int(r2), (r1 + r2) / 2) for k, [r1, r2] in _stats.items()}
        stats = dict(sorted(stats.items(), key=lambda x: x[1][2], reverse=True))

        if self.pretty_print:
            for (res, [r1, r2, avg]) in stats.items():
                print(f"{res.replace('BenchmarkResult.', '')}: {Percent(avg, self.total)}")
                print(f"\tResult 1: {Percent(r1, self.total)} ({r1} / {self.total})")
                print(f"\tResult 2: {Percent(r2, self.total)} ({r2} / {self.total})")
            return

        print("Result\tResult 1\tResult 2\tTotal\tResult 1 %\tResult 2 %\tAverage %")
        for (res, (r1, r2, avg)) in stats.items():
            print(f"{res.replace('BenchmarkResult.', '')}\t{r1}\t{r2}\t{self.total}\t{Percent(r1, self.total)}"
                  f"\t{Percent(r2, self.total)}\t{Percent(avg, self.total)}")

    def parse_template(self, results1: list, results2: list) -> dict[int, tuple[int, int, int, float]]:
        _template_stats: dict[int, list[int | float]] = defaultdict(lambda: [0, 0, 0, 0.0])

        for results, idx in [(results1, 0), (results2, 1)]:
            for res in results:
                if res["template"] in self.exclude:
                    continue

                if idx == 0:
                    _template_stats[res["template"]][2] += 1

                if res["result"] == "BenchmarkResult.CORRECT":
                    _template_stats[res["template"]][idx] += 1

        template_stats = {k: (int(r1), int(r2), int(t), (r1 + r2) / 2) for k, [r1, r2, t, _] in
                          _template_stats.items()}

        return dict(sorted(template_stats.items()))

    def template_results(self):
        results1, results2, *_ = self.results

        template_stats = self.parse_template(results1, results2)

        if self.pretty_print:
            for (template, (r1, r2, total, avg)) in template_stats.items():
                print(f"Template {template + 1}: {Percent(avg, total)}")
                print(f"\tResult 1: {Percent(r1, total)} ({r1} / {total})")
                print(f"\tResult 2: {Percent(r2, total)} ({r2} / {total})")
            return

        print("Template\tResult 1\tResult 2\tTotal\tResult 1 %\tResult 2 %\tAverage %")
        for (template, (r1, r2, total, avg)) in template_stats.items():
            print(f"{template + 1}\t{r1}\t{r2}\t{total}\t{Percent(r1, total)}\t{Percent(r2, total)}"
                  f"\t{Percent(avg, total)}")

    def template_diff(self):
        results1, results2, results1c, results2c = self.results
        template_stats_1 = self.parse_template(results1, results2)
        template_stats_2 = self.parse_template(results1c, results2c)

        # noinspection unresolved-references
        template_stats = {
            k: (a[3], b[3], a[2])
            for k, a in template_stats_1.items()
            if (b := template_stats_2.get(k)) is not None and a[3] != b[3]
        }

        if self.pretty_print:
            for (template, (avg1, avg2, total)) in template_stats.items():
                print(f"Template {template + 1}: {Percent(avg2, total) - Percent(avg1, total)}")
                print(f"\tResult 1: {Percent(avg1, total)}")
                print(f"\tResult 2: {Percent(avg2, total)}")
            return

        print("Template\tResult 1 %\tResult 2 %\t% Points Difference")
        for (template, (avg1, avg2, total)) in template_stats.items():
            print(f"{template + 1}\t{Percent(avg1, total)}\t{Percent(avg2, total)}"
                  f"\t{Percent(avg2, total) - Percent(avg1, total)}")
