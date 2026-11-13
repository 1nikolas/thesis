import random
import string
from collections import defaultdict

from neo4j import GraphDatabase

SITE_COUNT = 20
ID_DIGITS = 10

SINGLE_STAGE_RATE = 0.18

BACKUP_RATE = 0.55

NEO4J_URI = 'neo4j+ssc://xxx.databases.neo4j.io'
NEO4J_AUTH = ('neo4j', 'xxx')

LABELS = ["SITE", "OLT", "CARD", "PORT", "PON_PORT",
          "SPLITTER", "SUB_SPLITTER", "ONT", "CABIN"]

DATE_PROPS = {"install_date"}

VENDORS = {"Huawei": ["MA5800-X7", "MA5800-X15"],
           "Nokia": ["7360 ISAM FX-8", "7360 ISAM FX-16"],
           "ZTE": ["C320", "C600"],
           "Calix": ["E7-2", "E9-2"]}
CARD_TYPES = ["GPON-8", "GPON-16", "XGS-PON-8"]
STREETS = ["Ermou", "Stadiou", "Patission", "Kifisias", "Syngrou",
           "Alexandras", "Vouliagmenis", "Mesogeion", "Piraeus", "Athinon"]


class MockupGenerator:
    def __init__(self):
        self.__neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)
        self.__neo4j_session = self.__neo4j_driver.session()
        self.__used_ids = set()

        # label -> [{name: ..., prop: ...}, ...]
        self.__nodes = defaultdict(list)
        # (left_label, relation, right_label) -> [(left_name, right_name), ...]
        self.__edges = defaultdict(list)

        self.__sites = [
            "Athens", "Thessaloniki", "Patras", "Heraklion", "Larissa", "Volos",
            "Rhodes", "Ioannina", "Chania", "Agrinio", "Chalkis", "Katerini",
            "Trikala", "Serres", "Lamia", "Alexandroupoli", "Kozani", "Kavala",
            "Veria", "Corinth", "Drama", "Rethymno", "Komotini", "Mytilene",
            "Tripoli", "Kalamata", "Chios", "Corfu", "Sparta", "Xanthi"
        ]
        assert SITE_COUNT <= len(self.__sites), "not enough site names"

    def close(self):
        self.__neo4j_session.close()
        self.__neo4j_driver.close()

    def __get_random_id(self) -> str:
        while True:
            new_id = ''.join(random.choices(string.digits, k=ID_DIGITS))
            if new_id not in self.__used_ids and not new_id.startswith("0"):
                self.__used_ids.add(new_id)
                return new_id

    def __get_random_site(self) -> str:
        site = random.choice(self.__sites)
        self.__sites.remove(site)
        return site

    def __random_date(self, start_year=2016, end_year=2025) -> str:
        year = random.randint(start_year, end_year)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        return f"{year:04d}-{month:02d}-{day:02d}"

    def __add_node(self, label: str, name: str, **props) -> str:
        self.__nodes[label].append({"name": name, **props})
        return name

    def __add_edge(self, left_label, left, relation, right_label, right):
        self.__edges[(left_label, relation, right_label)].append((left, right))

    def __add_ont(self, parent: str, parent_label: str) -> str:
        status = random.choices(["active", "inactive", "faulty"], [0.86, 0.09, 0.05])[0]

        signal = round(random.uniform(-31.0, -26.0) if status == "faulty"
                       else random.uniform(-27.0, -17.0), 1)
        ont = self.__add_node("ONT", self.__get_random_id(),
                              status=status,
                              signal_dbm=signal,
                              install_date=self.__random_date())
        self.__add_edge("ONT", ont, "CONNECTS_TO", parent_label, parent)
        return ont

    def __build(self):
        for _ in range(SITE_COUNT):
            site = self.__get_random_site()
            self.__add_node("SITE", site)

            splitters_in_site = []

            for _ in range(random.randint(1, 3)):
                vendor = random.choice(list(VENDORS))
                olt = self.__add_node("OLT", self.__get_random_id(),
                                      vendor=vendor,
                                      model=random.choice(VENDORS[vendor]),
                                      capacity=random.choice([1024, 2048, 4096]))
                self.__add_edge("OLT", olt, "IN_SITE", "SITE", site)

                for card_slot in range(random.randint(1, 4)):
                    card = self.__add_node("CARD", self.__get_random_id(),
                                           slot=card_slot,
                                           card_type=random.choice(CARD_TYPES))
                    self.__add_edge("CARD", card, "CONNECTS_TO", "OLT", olt)

                    for port_slot in range(random.randint(2, 6)):
                        port = self.__add_node("PORT", self.__get_random_id(),
                                               slot=port_slot,
                                               admin_state=random.choices(
                                                   ["enabled", "disabled"],
                                                   [0.93, 0.07])[0])
                        self.__add_edge("PORT", port, "CONNECTS_TO", "CARD", card)

                        pon = self.__add_node("PON_PORT", self.__get_random_id())
                        self.__add_edge("PON_PORT", pon, "CONNECTS_TO", "PORT", port)

                        splitter = self.__add_node("SPLITTER", self.__get_random_id(),
                                                   split_ratio=random.choice([8, 16, 32]),
                                                   install_date=self.__random_date())
                        self.__add_edge("SPLITTER", splitter, "CONNECTS_TO",
                                        "PON_PORT", pon)
                        splitters_in_site.append(splitter)

                        if random.random() < SINGLE_STAGE_RATE:
                            for _ in range(int(random.triangular(1, 12, 3))):
                                self.__add_ont(splitter, "SPLITTER")

                        for _ in range(random.randint(1, 8)):
                            sub = self.__add_node("SUB_SPLITTER", self.__get_random_id(),
                                                  split_ratio=random.choice([8, 16]))
                            self.__add_edge("SUB_SPLITTER", sub, "CONNECTS_TO",
                                            "SPLITTER", splitter)

                            if random.random() < 0.06:
                                continue
                            for _ in range(int(random.triangular(1, 16, 4))):
                                self.__add_ont(sub, "SUB_SPLITTER")

            cabins_in_site = []
            if splitters_in_site:
                num_cabins = random.randint(1, min(3, len(splitters_in_site)))
                random.shuffle(splitters_in_site)
                covered = splitters_in_site[:int(len(splitters_in_site) * 0.9)]
                per_cabin = max(1, len(covered) // num_cabins)

                for cab in range(num_cabins):
                    cabin = self.__add_node("CABIN", self.__get_random_id(),
                                            street=random.choice(STREETS),
                                            capacity=random.choice([24, 48, 96]))
                    cabins_in_site.append(cabin)
                    start = cab * per_cabin
                    end = len(covered) if cab == num_cabins - 1 else start + per_cabin
                    for splitter in covered[start:end]:
                        self.__add_edge("CABIN", cabin, "CONNECTS_TO",
                                        "SPLITTER", splitter)

            if len(cabins_in_site) > 1:
                for cabin in cabins_in_site:
                    if random.random() < BACKUP_RATE:
                        other = random.choice([c for c in cabins_in_site if c != cabin])
                        self.__add_edge("CABIN", cabin, "BACKUP_FOR", "CABIN", other)


    def __clear_database(self):
        self.__neo4j_session.run("MATCH (n) DETACH DELETE n")
        for label in LABELS:
            self.__neo4j_session.run(
                f"CREATE INDEX idx_{label.lower()}_name IF NOT EXISTS "
                f"FOR (n:{label}) ON (n.name)"
            )

    def __write(self, batch_size: int = 5000):
        """One round-trip per batch instead of one per node."""
        for label, rows in self.__nodes.items():
            date_props = DATE_PROPS & set(rows[0])
            casts = "".join(f" SET n.{p} = date(row.{p})" for p in sorted(date_props))
            for i in range(0, len(rows), batch_size):
                self.__neo4j_session.run(
                    f"UNWIND $rows AS row CREATE (n:{label}) SET n = row{casts}",
                    rows=rows[i:i + batch_size],
                )
            print(f"wrote {len(rows):6d} {label}")

        for (left_label, relation, right_label), pairs in self.__edges.items():
            for i in range(0, len(pairs), batch_size):
                self.__neo4j_session.run(
                    f"""
                    UNWIND $pairs AS pair
                    MATCH (a:{left_label} {{name: pair[0]}})
                    MATCH (b:{right_label} {{name: pair[1]}})
                    CREATE (a)-[:{relation}]->(b)
                    """,
                    pairs=[list(p) for p in pairs[i:i + batch_size]],
                )
            print(f"wrote {len(pairs):6d} ({left_label})-[:{relation}]->({right_label})")


    def report(self):
        print("\n--- node counts ---")
        total = 0
        for label in LABELS:
            rows = self.__nodes[label]
            names = [r["name"] for r in rows]
            total += len(names)
            unique = "ok" if len(set(names)) == len(names) else "** DUPES **"
            props = ", ".join(k for k in rows[0] if k != "name") or "-"
            print(f"  {label:14s} {len(names):6d}  names {unique:10s}  props: {props}")
        print(f"  {'TOTAL':14s} {total:6d}")

        print("\n--- edges ---")
        for (left, rel, right), pairs in sorted(self.__edges.items()):
            print(f"  {len(pairs):6d}  (:{left})-[:{rel}]->(:{right})")

        parent = {}
        for (left_label, relation, right_label), pairs in self.__edges.items():
            if left_label == "CABIN":
                continue
            for left, right in pairs:
                parent[(left_label, left)] = (right_label, right)

        ont_counts = defaultdict(int)
        depths = defaultdict(int)
        for row in self.__nodes["ONT"]:
            node, depth = ("ONT", row["name"]), 0
            ont_counts[node] += 1
            while node in parent:
                node = parent[node]
                depth += 1
                ont_counts[node] += 1
                if node[0] == "OLT":
                    depths[depth] += 1
        for cabin, splitter in self.__edges[("CABIN", "CONNECTS_TO", "SPLITTER")]:
            ont_counts[("CABIN", cabin)] += ont_counts[("SPLITTER", splitter)]

        print("\n--- 'which X serves the most ONTs?' — is the answer unique? ---")
        for label in ["SITE", "OLT", "CABIN", "CARD", "PORT", "PON_PORT",
                      "SPLITTER", "SUB_SPLITTER"]:
            counts = [ont_counts[(label, r["name"])] for r in self.__nodes[label]]
            if not counts:
                continue
            top = max(counts)
            tied = counts.count(top)
            verdict = "USABLE" if tied == 1 else f"tie x{tied}, avoid"
            print(f"  {label:14s} n={len(counts):5d}  max={top:5d}  {verdict}")

        print("\n--- ONT -> OLT depth ---")
        for depth, count in sorted(depths.items()):
            print(f"  {depth} hops: {count} ONTs")

        print("\n--- property distributions ---")
        for label, prop in [("ONT", "status"), ("PORT", "admin_state"),
                            ("SPLITTER", "split_ratio"), ("OLT", "vendor")]:
            counts = defaultdict(int)
            for row in self.__nodes[label]:
                counts[row[prop]] += 1
            print(f"  {label}.{prop}: {dict(sorted(counts.items(), key=str))}")

        print("\n--- absence questions must not be trivially empty ---")
        subs_with_onts = {p[1] for p in self.__edges[("ONT", "CONNECTS_TO", "SUB_SPLITTER")]}
        empty_subs = len(self.__nodes["SUB_SPLITTER"]) - len(subs_with_onts)
        cabled = {p[1] for p in self.__edges[("CABIN", "CONNECTS_TO", "SPLITTER")]}
        orphan = len(self.__nodes["SPLITTER"]) - len(cabled)
        print(f"  SUB_SPLITTERs with no ONT : {empty_subs}")
        print(f"  SPLITTERs with no CABIN   : {orphan}")

    def generate(self):
        self.__build()
        self.__clear_database()
        self.__write()
        self.report()


if __name__ == "__main__":
    generator = MockupGenerator()

    generator.generate()

    generator.close()