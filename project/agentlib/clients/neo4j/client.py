from neo4j import GraphDatabase, Record, NotificationSeverity, NotificationClassification
from ..base_client import BaseClient
import logging

logging.getLogger("neo4j.notifications").setLevel(logging.ERROR)

class QueryRes:
    def __init__(self, records: list[Record], warnings: list[str]) -> None:
        self.records = records
        self.warnings = warnings


class Neo4jClient(BaseClient):
    def __init__(self, creds: tuple):
        self.driver = GraphDatabase.driver(creds[0], auth=(creds[1], creds[2]))

    def close(self):
        self.driver.close()

    def query(self, query: str) -> QueryRes:
        with self.driver.session() as session:
            with session.begin_transaction(timeout=60) as tx:
                result = tx.run(query)
                records = list(result)
                summary = result.consume()

                warnings = [
                    obj.status_description
                    for obj in summary.gql_status_objects
                    if obj.severity == NotificationSeverity.WARNING and obj.classification == NotificationClassification.UNRECOGNIZED
                ]

                return QueryRes(records, warnings)
