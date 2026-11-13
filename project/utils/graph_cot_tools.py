from agentlib.clients import Neo4jClient


class GraphCotTools:
    def __init__(self, neo4j_client: Neo4jClient):
        self.neo4j = neo4j_client

    def run(self, name: str, args: str) -> str:
        try:
            key = name.lower()
            if key == "retrievenode":
                return self.retrieve_node(args)
            if key == "nodefeature":
                node_id, feature = self._split2(args)
                return self.node_feature(node_id, feature)
            if key in ("neighborcheck", "neighbourcheck"):
                node_id, ntype = self._split2(args)
                return self.neighbor_check(node_id, ntype)
            if key == "nodedegree":
                node_id, ntype = self._split2(args)
                return self.node_degree(node_id, ntype)
            return (f"Unknown function '{name}'. Valid functions: RetrieveNode, "
                    "NodeFeature, NeighborCheck, NodeDegree.")
        except ValueError as e:
            return f"Bad arguments for {name}[{args}]: {e}"
        except Exception as e:
            return f"Error running {name}[{args}]: {e}"

    @staticmethod
    def _split2(args: str):
        parts = args.split(",", 1)
        if len(parts) != 2:
            raise ValueError("expected two comma-separated arguments")
        return parts[0].strip(), parts[1].strip()

    @staticmethod
    def _esc(value: str) -> str:
        return value.replace("\\", "\\\\").replace('"', '\\"')

    @staticmethod
    def _id_property(properties: list) -> str:
        if len(properties) == 1:
            return properties[0]

        return (
                next((p for p in properties if p.endswith("Id")), None)
                or next((p for p in properties if p.endswith("No")), None)
                or next((p for p in properties if p == "name"), None)
                or properties[0]
        )

    def retrieve_node(self, keyword: str) -> str:
        cypher = (
            'MATCH (n) '
            'WITH n, [k IN keys(n) WHERE toLower(toString(n[k])) = '
            f'"{self._esc(keyword.lower())}"] AS props '
            'WHERE props <> [] '
            'RETURN elementId(n) AS id, labels(n) AS labels, '
            'props, n AS node '
            'LIMIT 5'
        )
        rows = self.neo4j.query(cypher).records
        if not rows:
            return f"No node found with a property value of '{keyword}'."
        out = []
        for r in rows:
            d = r.data()
            matched_props = [f'{prop}={d["node"].get(prop, "?")}' for prop in d["props"]]
            out.append(f'id={d["id"]} labels={d["labels"]} {' '.join(matched_props)}')
        return "Found: " + "; ".join(out)

    def node_feature(self, node_id: str, feature: str) -> str:
        if feature.lower() in ("labels", "label", "type"):
            cypher = (
                f'MATCH (n) WHERE elementId(n) = "{self._esc(node_id)}" '
                'RETURN labels(n) AS labels'
            )
            rows = self.neo4j.query(cypher).records
            if not rows:
                return f"No node with id {node_id}."
            return f"labels: {rows[0].data()['labels']}"

        cypher = (
            f'MATCH (n) WHERE elementId(n) = "{self._esc(node_id)}" '
            'RETURN properties(n) AS props'
        )
        rows = self.neo4j.query(cypher).records
        if not rows:
            return f"No node with id {node_id}."
        props = rows[0].data()["props"]
        if feature in props:
            return f"{feature}: {props[feature]}"
        return (f"Node {node_id} has no feature '{feature}'. "
                f"Available features: {', '.join(props.keys())} "
                "(use 'labels' to see the node's type).")

    def neighbor_check(self, node_id: str, ntype: str) -> str:
        t = self._esc(ntype)
        cypher = (
            f'MATCH (n)-[r]-(m) WHERE elementId(n) = "{self._esc(node_id)}" '
            f'AND (type(r) = "{t}" OR "{t}" IN labels(m)) '
            'RETURN elementId(m) AS id, m AS node, labels(m) AS labels, keys(m) AS props, '
            "type(r) AS rel, properties(r) AS relProps, CASE WHEN startNode(r) = n THEN 'from' ELSE 'to' END AS dir "
        )
        rows = [r.data() for r in self.neo4j.query(cypher).records]
        if not rows:
            return (f"Node {node_id} has no '{ntype}' neighbors "
                    "(try a different label/relationship type).")
        parts = []
        for d in rows:
            prop = self._id_property(d["props"])
            rel_props = ", ".join(f"{k}={v}" for k, v in d["relProps"].items())

            parts.append((f'{prop}={d["node"].get(prop, "?")} (id={d["id"]}, labels={d["labels"]}, '
                          f'{d["rel"]}{f" ({rel_props})" if rel_props else ""} {d["dir"]} this node)'))
        return f"'{ntype}' neighbors of {node_id}: " + "; ".join(parts)

    def node_degree(self, node_id: str, ntype: str) -> str:
        t = self._esc(ntype)
        cypher = (
            f'MATCH (n)-[r]-(m) WHERE elementId(n) = "{self._esc(node_id)}" '
            f'AND (type(r) = "{t}" OR "{t}" IN labels(m)) '
            'RETURN count(DISTINCT m) AS degree'
        )
        rows = self.neo4j.query(cypher).records
        degree = rows[0].data()["degree"] if rows else 0
        return f"Node {node_id} has {degree} '{ntype}' neighbors."
