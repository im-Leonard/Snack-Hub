import mysql.connector
from mysql.connector import pooling

from snackhub2.config import DB_CONFIG


class Database:
    def __init__(self, config: dict):
        self._config = dict(config)
        self._pool: pooling.MySQLConnectionPool | None = None

    def get_pool(self) -> pooling.MySQLConnectionPool | None:
        if self._pool is None:
            try:
                self._pool = pooling.MySQLConnectionPool(
                    pool_name="snackhub_pool",
                    pool_size=10,
                    **self._config,
                )
            except Exception as e:
                print(f"Warnung: Konnte nicht zu MySQL verbinden: {e}")
                return None
        return self._pool

    def get_conn(self):
        p = self.get_pool()
        if p is None:
            raise Exception("Keine Datenbankverbindung verfügbar")
        return p.get_connection()

_db = Database(DB_CONFIG)

def get_pool():
    return _db.get_pool()

def get_conn():
    return _db.get_conn()
