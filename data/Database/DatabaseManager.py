import psycopg2
import os
from psycopg2._psycopg import cursor


# Marc Kluge
class DatabaseManager:
    def __init__(self):  # Stellt die Datenbankanbindung her
        self.conn = psycopg2.connect(
            host='localhost',
            database='postgres',
            user=os.environ["DB_USERNAME"],
            password=os.environ["DB_PASSWORD"]
        )
        self.cur = self.conn.cursor()

    def execute_query(self, query: str, params: object = None) -> cursor:
        self.cur.execute(query, params)
        return self.cur

    def close(self):
        self.cur.close()
        self.conn.close()

    def commit_and_close(self):
        self.conn.commit()
        self.cur.close()
        self.conn.close()

