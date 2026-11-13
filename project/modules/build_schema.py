import json
from collections import defaultdict, deque, namedtuple
from typing import Iterable, List
from neo4j import GraphDatabase

from utils import get_dataset_creds

Schema = namedtuple("Schema", ["left_node", "relation", "right_node", "min_hops", "max_hops"])
MAX_HOPS = 25
APOC_QUERY = "CALL apoc.meta.schema() YIELD value RETURN value"


class BuildSchema:
    def __init__(self, dataset: str) -> None:
        self.dataset = dataset

        self.generate()

    @staticmethod
    def direct_edges_from_apoc(apoc_schema: dict) -> List[tuple]:
        edges = set()
        for label, info in apoc_schema.items():
            if info.get("type") != "node":
                continue
            for relation, rel_info in info.get("relationships", {}).items():
                for other in rel_info.get("labels", []):
                    if rel_info.get("direction") == "out":
                        edges.add((label, relation, other))
                    elif rel_info.get("direction") == "in":
                        edges.add((other, relation, label))
        return sorted(edges)

    @staticmethod
    def _is_acyclic(graph: dict) -> bool:
        white, grey, black = 0, 1, 2
        color = defaultdict(int)

        def visit(node) -> bool:
            color[node] = grey
            for nxt in graph.get(node, ()):
                if color[nxt] == grey:
                    return False
                if color[nxt] == white and not visit(nxt):
                    return False
            color[node] = black
            return True

        return all(color[n] != white or visit(n) for n in list(graph))

    @staticmethod
    def build_schema(direct_edges: Iterable[tuple]) -> List[Schema]:
        direct_edges = set(direct_edges)

        adjacency = defaultdict(lambda: defaultdict(set))
        for left, relation, right in direct_edges:
            adjacency[relation][left].add(right)

        schemas = []

        for relation, graph in adjacency.items():
            acyclic = BuildSchema._is_acyclic(graph)
            labels = set(graph) | {d for outs in graph.values() for d in outs}

            for source in labels:
                mins, queue = {}, deque([(source, 0)])
                while queue:
                    node, dist = queue.popleft()
                    if dist >= MAX_HOPS:
                        continue
                    for nxt in graph.get(node, ()):
                        if nxt not in mins or dist + 1 < mins[nxt]:
                            mins[nxt] = dist + 1
                            queue.append((nxt, dist + 1))

                maxs = {}
                if acyclic:
                    stack = [(source, 0, frozenset([source]))]
                    while stack:
                        node, dist, seen = stack.pop()
                        if dist >= MAX_HOPS:
                            continue
                        for nxt in graph.get(node, ()):
                            if nxt in seen:
                                continue
                            maxs[nxt] = max(maxs.get(nxt, 0), dist + 1)
                            stack.append((nxt, dist + 1, seen | {nxt}))

                for target, low in mins.items():
                    high = maxs.get(target, low) if acyclic else None
                    schemas.append(Schema(source, relation, target, low, high))

        return sorted(schemas)

    @staticmethod
    def node_properties_from_apoc(apoc_schema: dict) -> list:
        return [
            f"(:{label}) " + ", ".join(
                f"{name}: {prop.get('type', 'UNKNOWN')}"
                for name, prop in sorted(info.get("properties", {}).items())
            )
            for label, info in sorted(apoc_schema.items())
            if info.get("type") == "node"
        ]

    @staticmethod
    def relationship_properties_from_apoc(apoc_schema: dict) -> list:
        return [
            f"(:{label}) " + ", ".join(
                f"{name}: {prop.get('type', 'UNKNOWN')}"
                for name, prop in sorted(info.get("properties", {}).items())
            )
            for label, info in sorted(apoc_schema.items())
            if info.get("type") == "relationship"
        ]

    @staticmethod
    def get_connections(schema) -> list[str]:
        connections = []

        for left, relation, right, min_hops, max_hops in schema:
            if max_hops is None:
                quantifiers = [f"*{min_hops}.."]
                if min_hops == 1:
                    quantifiers.insert(0, "")
            elif min_hops == max_hops:
                quantifiers = ["" if min_hops == 1 else f"*{min_hops}"]
            else:
                quantifiers = ["" if h == 1 else f"*{h}"
                               for h in range(min_hops, max_hops + 1)]
                quantifiers.append(f"*{min_hops}..{max_hops}")

            for quantifier in quantifiers:
                connections.append(f"(:{left})-[:{relation}{quantifier}]->(:{right})")

        return sorted(connections)

    @staticmethod
    def get_simple_connections(direct_edges) -> list[str]:
        return sorted(
            f"{left} -> {right}  using relation {relation}"
            for left, relation, right in direct_edges
        )

    def generate(self) -> None:
        neo_uri, neo_user, neo_pass = get_dataset_creds(self.dataset)
        driver = GraphDatabase.driver(neo_uri, auth=(neo_user, neo_pass))

        with driver.session() as session:
            query_res = session.run(APOC_QUERY).single()

            if not query_res:
                print("Get schema error!")
                exit(1)

            meta = query_res["value"]

        driver.close()

        direct_edges = BuildSchema.direct_edges_from_apoc(meta)
        schema = BuildSchema.build_schema(direct_edges)

        nodes = BuildSchema.node_properties_from_apoc(meta)
        relations = BuildSchema.relationship_properties_from_apoc(meta)
        connections = BuildSchema.get_connections(schema)
        simple_connections = BuildSchema.get_simple_connections(direct_edges)

        full_schema = {'nodes': nodes, 'relations': relations, 'connections': connections,
                       'simple_connections': simple_connections, 'schema': schema}

        path = f"../data/{self.dataset}/schema.json"

        with open(path, "w") as f:
            f.write(json.dumps(full_schema))

        print(f"Saved on {path}!")
