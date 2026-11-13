"""
Code adapted and reworked from:
https://github.com/sakusaku-rich/cypher-direction-competition
"""

import re
from collections import namedtuple
from typing import Any, Dict, List, Optional, Tuple

Schema = namedtuple("Schema", ["left_node", "relation", "right_node", "min_hops", "max_hops"])

_quantifier_pattern = re.compile(r"\*\s*(\d*)\s*(\.\.)?\s*(\d*)")

_BRACKET = (r"\[\s*\w*\s*(?::\s*[\w|`]+)?\s*"
            r"(?:\*\s*\d*(?:\s*\.\.\s*\d*)?)?\s*(?:\{.*})?\s*]")

_strict_relation_pattern = re.compile(
    rf"^(?:-{_BRACKET}->|<-{_BRACKET}-|-{_BRACKET}-)$"
)

_type_list_pattern = re.compile(r"(\[\s*\w*\s*:\s*[\w|`]+)(\*[^]{\s]*)?")

MALFORMED = [
    (re.compile(r"-(\[[^]]*])<-"), r"<-\1-"),  # -[:R]<-  ->  <-[:R]-
    (re.compile(r"->(\[[^]]*])-"), r"-\1->"),  # ->[:R]-  ->  -[:R]->
    (re.compile(r"<-(\[[^]]*])<-"), r"<-\1-"),  # <-[:R]<- ->  <-[:R]-
    (re.compile(r"->(\[[^]]*])->"), r"-\1->"),  # ->[:R]-> ->  -[:R]->
]


class CorrectorRes:
    def __init__(self, res: str, has_error=False):
        self.res = res
        self.has_error = has_error


def fix_arrows(query: str) -> str:
    for pattern, replacement in MALFORMED:
        query = pattern.sub(replacement, query)
    return query


def quantifier(min_hops: int, max_hops: Optional[int]) -> str:
    if min_hops == 1 and max_hops == 1:
        return ""
    if max_hops is None:
        return f"*{min_hops}.."
    if min_hops == max_hops:
        return f"*{min_hops}"
    return f"*{min_hops}..{max_hops}"


def parse_quantifier(relation_type: str) -> Tuple[int, Optional[int]]:
    found = _quantifier_pattern.search(relation_type)
    if not found:
        return 1, 1
    low, dots, high = found.groups()
    if not dots:
        return (int(low), int(low)) if low else (1, None)
    return int(low) if low else 1, int(high) if high else None


def fits(written: Tuple[int, Optional[int]],
         allowed: Tuple[int, Optional[int]]) -> bool:
    written_low, written_high = written
    allowed_low, allowed_high = allowed
    if written_low < allowed_low:
        return False
    if allowed_high is None:
        return True
    return written_high is not None and written_high <= allowed_high


def describe_labels(labels: List[str]) -> str:
    return ":" + "|".join(labels) if labels else "<unlabelled>"


def describe_relations(relation_types: List[str]) -> str:
    return "|".join(relation_types) if relation_types else "<any>"


def pattern_of(schema: Schema) -> str:
    left, relation, right, low, high = schema
    return f"(:{left})-[:{relation}{quantifier(low, high)}]->(:{right})"


def trim(items: List[str], limit: int) -> str:
    shown = ", ".join(items[:limit])
    return shown + (f" (and {len(items) - limit} more)" if len(items) > limit else "")


class CypherQueryCorrector:
    property_pattern = re.compile(r"\{.+?}")
    node_pattern = re.compile(r"\(.+?\)")
    path_pattern = re.compile(
        r"(\([^,()]*?(\{.+})?[^,()]*?\))(<?-)(\[.*?])?(->?)(\([^,()]*?(\{.+})?[^,()]*?\))"
    )
    node_relation_node_pattern = re.compile(
        r"(\()+(?P<left_node>[^()]*?)\)(?P<relation>.*?)\((?P<right_node>[^()]*?)(\))+"
    )
    relation_type_pattern = re.compile(r":(?P<relation_type>.+?)?(\{.+})?]")

    def __init__(self, schemas: List[Schema]):
        self.schemas = schemas

    def clean_node(self, node: str) -> str:
        node = re.sub(self.property_pattern, "", node)
        node = node.replace("(", "")
        node = node.replace(")", "")
        node = node.strip()
        return node

    def detect_node_variables(self, query: str) -> Dict[str, List[str]]:
        nodes = re.findall(self.node_pattern, query)
        nodes = [self.clean_node(node) for node in nodes]
        res: Dict[str, Any] = {}
        for node in nodes:
            parts = node.split(":")
            if parts[0] == "":
                continue
            variable = parts[0]
            if variable not in res:
                res[variable] = []
            res[variable] += parts[1:]
        return res

    def extract_paths(self, query: str) -> "List[str]":
        paths = []
        idx = 0
        while matched := self.path_pattern.findall(query[idx:]):
            matched = matched[0]
            matched = [
                m for i, m in enumerate(matched) if i not in [1, len(matched) - 1]
            ]
            path = "".join(matched)
            idx = idx + query[idx:].find(path) + len(path) - len(matched[-1])
            paths.append(path)
        return paths

    @staticmethod
    def judge_direction(relation: str) -> str:
        direction = "BIDIRECTIONAL"
        if relation[0] == "<":
            direction = "INCOMING"
        if relation[-1] == ">":
            direction = "OUTGOING"
        return direction

    @staticmethod
    def extract_node_variable(part: str) -> Optional[str]:
        part = part.lstrip("(").rstrip(")")
        idx = part.find(":")
        if idx != -1:
            part = part[:idx]
        return None if part == "" else part

    def detect_labels(
            self, str_node: str, node_variable_dict: Dict[str, Any]
    ) -> List[str]:
        str_node = re.sub(self.property_pattern, "", str_node).strip()
        splitted_node = str_node.split(":")
        variable = splitted_node[0]
        labels = []
        if variable in node_variable_dict:
            labels = node_variable_dict[variable]
        elif variable == "" and len(splitted_node) > 1:
            labels = splitted_node[1:]
        return labels

    def match_schema(
            self,
            from_node_labels: List[str],
            relation_types: List[str],
            to_node_labels: List[str],
    ) -> List[Schema]:
        valid_schemas = self.schemas
        if from_node_labels:
            from_node_labels = [label.strip("`") for label in from_node_labels]
            valid_schemas = [
                schema for schema in valid_schemas if schema[0] in from_node_labels
            ]
        if to_node_labels:
            to_node_labels = [label.strip("`") for label in to_node_labels]
            valid_schemas = [
                schema for schema in valid_schemas if schema[2] in to_node_labels
            ]
        if relation_types:
            relation_types = [rel_type.strip("`") for rel_type in relation_types]
            valid_schemas = [
                schema for schema in valid_schemas if schema[1] in relation_types
            ]
        return valid_schemas

    def verify_schema(
            self,
            from_node_labels: List[str],
            relation_types: List[str],
            to_node_labels: List[str],
    ) -> bool:
        return self.match_schema(from_node_labels, relation_types, to_node_labels) != []

    def explain_mismatch(
            self,
            from_node_labels: List[str],
            relation_types: List[str],
            to_node_labels: List[str],
            limit: int = 6,
    ) -> str:
        left, right = set(from_node_labels), set(to_node_labels)

        between = sorted({pattern_of(s) for s in self.schemas
                          if (not left or s[0] in left or s[2] in left)
                          and (not right or s[0] in right or s[2] in right)})
        if between:
            return "these labels are connected by: " + trim(between, limit)

        by_type = sorted({pattern_of(s) for s in self.schemas
                          if s[1] in relation_types})
        if by_type:
            return (f"[:{describe_relations(relation_types)}] only connects: "
                    + trim(by_type, limit))

        return "no relationship in the schema involves these labels"

    def mismatch_error(
            self,
            from_node_labels: List[str],
            relation_types: List[str],
            to_node_labels: List[str],
    ) -> CorrectorRes:
        return CorrectorRes(
            f"No relationship [:{describe_relations(relation_types)}] between "
            f"({describe_labels(from_node_labels)}) and "
            f"({describe_labels(to_node_labels)}) in either direction; "
            + self.explain_mismatch(from_node_labels, relation_types, to_node_labels),
            True,
        )

    def detect_relation_types(self, str_relation: str) -> Tuple[str, List[str]]:
        relation_direction = self.judge_direction(str_relation)
        relation_type = self.relation_type_pattern.search(str_relation)
        if relation_type is None or relation_type.group("relation_type") is None:
            return relation_direction, []
        relation_types = [
            t.strip().strip("!")
            for t in relation_type.group("relation_type").split("|")
        ]
        return relation_direction, relation_types

    def correct_query(self, query: str) -> CorrectorRes:
        query_fixed = fix_arrows(query)

        node_variable_dict = self.detect_node_variables(query_fixed)
        paths = self.extract_paths(query_fixed)

        for path in paths:
            original_path = path
            start_idx = 0
            while start_idx < len(path):
                match_res = re.match(self.node_relation_node_pattern, path[start_idx:])
                if match_res is None:
                    break
                start_idx += match_res.start()
                match_dict = match_res.groupdict()
                left_node_labels = self.detect_labels(
                    match_dict["left_node"], node_variable_dict
                )
                right_node_labels = self.detect_labels(
                    match_dict["right_node"], node_variable_dict
                )
                end_idx = (
                        start_idx
                        + 4
                        + len(match_dict["left_node"])
                        + len(match_dict["relation"])
                        + len(match_dict["right_node"])
                )
                original_partial_path = original_path[start_idx: end_idx + 1]

                if not _strict_relation_pattern.match(match_dict["relation"]):
                    return CorrectorRes(
                        f"Malformed relationship pattern '{match_dict['relation']}' in "
                        f"'{original_partial_path}'. Write it as -[:REL]-> or <-[:REL]-.",
                        True,
                    )

                relation_direction, relation_types = self.detect_relation_types(
                    match_dict["relation"]
                )

                relation_text = match_dict["relation"]

                relation_types_orig = relation_types.copy()

                for i in range(len(relation_types)):
                    relation_types[i] = relation_types[i].split("*")[0]

                if relation_direction == "OUTGOING":
                    is_legal = self.verify_schema(
                        left_node_labels, relation_types, right_node_labels
                    )
                    if not is_legal:
                        is_legal = self.verify_schema(
                            right_node_labels, relation_types, left_node_labels
                        )
                        if is_legal:
                            corrected_relation = "<" + match_dict["relation"][:-1]
                            relation_text = corrected_relation
                            corrected_partial_path = original_partial_path.replace(
                                match_dict["relation"], corrected_relation
                            )
                            query = query.replace(
                                original_partial_path, corrected_partial_path
                            )

                            original_partial_path = corrected_partial_path
                        else:
                            return self.mismatch_error(
                                left_node_labels, relation_types, right_node_labels
                            )
                elif relation_direction == "INCOMING":
                    is_legal = self.verify_schema(
                        right_node_labels, relation_types, left_node_labels
                    )
                    if not is_legal:
                        is_legal = self.verify_schema(
                            left_node_labels, relation_types, right_node_labels
                        )
                        if is_legal:
                            corrected_relation = match_dict["relation"][1:] + ">"
                            relation_text = corrected_relation
                            corrected_partial_path = original_partial_path.replace(
                                match_dict["relation"], corrected_relation
                            )
                            query = query.replace(
                                original_partial_path, corrected_partial_path
                            )

                            original_partial_path = corrected_partial_path
                        else:
                            return self.mismatch_error(
                                right_node_labels, relation_types, left_node_labels
                            )
                else:
                    is_legal = self.verify_schema(
                        left_node_labels, relation_types, right_node_labels
                    )

                    if is_legal:
                        corrected_relation = match_dict["relation"] + ">"
                        relation_text = corrected_relation
                        corrected_partial_path = original_partial_path.replace(
                            match_dict["relation"], corrected_relation
                        )
                        query = query.replace(
                            original_partial_path, corrected_partial_path
                        )

                        original_partial_path = corrected_partial_path
                    else:
                        is_legal = self.verify_schema(
                            right_node_labels, relation_types, left_node_labels
                        )

                        if is_legal:
                            corrected_relation = "<" + match_dict["relation"]
                            relation_text = corrected_relation
                            corrected_partial_path = original_partial_path.replace(
                                match_dict["relation"], corrected_relation
                            )
                            query = query.replace(
                                original_partial_path, corrected_partial_path
                            )

                            original_partial_path = corrected_partial_path
                        else:
                            return self.mismatch_error(
                                left_node_labels, relation_types, right_node_labels
                            )

                match = self.match_schema(left_node_labels, relation_types, right_node_labels)
                if not match:
                    match = self.match_schema(right_node_labels, relation_types, left_node_labels)

                written = parse_quantifier(relation_types_orig[0]) if relation_types_orig else (1, 1)
                allowed = {(m[3], m[4]) for m in match}

                if not any(fits(written, a) for a in allowed) and len(allowed) == 1:
                    quant = quantifier(*allowed.pop())
                    new_relation = _type_list_pattern.sub(
                        lambda m: m.group(1) + quant, relation_text, count=1
                    )

                    if new_relation != relation_text:
                        corrected_partial_path = original_partial_path.replace(
                            relation_text, new_relation, 1
                        )
                        query = query.replace(
                            original_partial_path, corrected_partial_path
                        )

                start_idx += (
                        len(match_dict["left_node"]) + len(match_dict["relation"]) + 2
                )
        return CorrectorRes(query)

    def __call__(self, query: str) -> CorrectorRes:
        return self.correct_query(query)
