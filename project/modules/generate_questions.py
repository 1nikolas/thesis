import json
import random

from neo4j import GraphDatabase

from utils import normalize_records, get_dataset_creds, get_templates, get_per_template, get_id_prop


class GenerateQuestions:
    def __init__(self, dataset):
        self.dataset = dataset

        self.generate()

    def _sample_targets(self, session) -> dict:
        targets = {t["needs"] for t in get_templates(self.dataset) if t["needs"]}
        sampled = {}

        for target in targets:
            if isinstance(target, tuple):
                label, prop = target
            else:
                label, prop = target, get_id_prop(self.dataset, target)
            rows = session.run(
                f"MATCH (n:{label}) WHERE n.{prop} IS NOT NULL "
                f"RETURN DISTINCT n.{prop} AS value ORDER BY rand() LIMIT $k", k=250)
            sampled[target] = [r["value"] for r in rows]

        return sampled

    @staticmethod
    def _viable_entities(session, template, pool, needed: int) -> list:
        if template.get("allow_empty") or not template["cypher"]:
            return random.sample(pool, min(needed, len(pool)))

        viable = []
        for entity in random.sample(pool, len(pool)):
            if session.run(template["cypher"].format(id=entity)).peek() is not None:
                viable.append(entity)
                if len(viable) >= needed:
                    return viable

        if not viable:
            return random.sample(pool, min(needed, len(pool)))
        return viable

    def build(self, session) -> list:
        sampled = self._sample_targets(session)

        rows, seen = [], set()
        qid = 0

        for template_id, template in enumerate(get_templates(self.dataset)):
            needs = template["needs"]
            pool = sampled.get(needs, []) if needs else [None]
            if needs and not pool:
                print(f"WARNING no values sampled for {needs}, skipping template")
                continue
            count = get_per_template(self.dataset) if needs else len(template["phrasings"])

            entities = (GenerateQuestions._viable_entities(session, template, pool, count)
                        if needs else [None])

            for i in range(count):
                phrasing = template["phrasings"][i % len(template["phrasings"])]

                question, entity = None, None
                for _ in range(len(entities) * 4):
                    entity = random.choice(entities)
                    candidate = (phrasing.format(id=entity) if entity is not None
                                 else phrasing)
                    if candidate not in seen:
                        question = candidate
                        break
                if question is None:
                    continue
                seen.add(question)

                gold = template["cypher"]
                answers = None
                if gold:
                    queries = [gold]
                    if template.get("alt_cypher"):
                        queries.append(template["alt_cypher"])
                    answers = []
                    for query in queries:
                        result = normalize_records([r.data() for r in session.run(
                            query.format(id=entity))])
                        if result not in answers:
                            answers.append(result)

                rows.append(dict(
                    qid=qid,
                    template=template_id,
                    question=question,
                    cypher=gold.format(id=entity) if gold else None,
                    answerable=gold is not None,
                    answers=answers,
                ))
                qid += 1

        random.shuffle(rows)
        return rows

    def generate(self):
        neo_uri, neo_user, neo_pass = get_dataset_creds(self.dataset)
        driver = GraphDatabase.driver(neo_uri, auth=(neo_user, neo_pass))
        with driver.session() as session:
            questions = self.build(session)
        driver.close()

        path = f"../data/{self.dataset}/questions.json"

        with open(path, "w") as f:
            f.write(json.dumps(questions))

        print(f"Saved on {path}!")
