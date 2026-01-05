from __future__ import annotations
import sqlite3, json
from typing import Any, Optional, Dict, List

class AgentMemory:
    def read(self, namespace: str, key: str) -> Optional[Any]: ...
    def write(self, namespace: str, key: str, value: Any, ttl: int | None = None) -> None: ...
    def append_log(self, namespace: str, record: Dict[str, Any]) -> None: ...

class SQLiteAgentMemory(AgentMemory):
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init()

    def _conn(self):
        return sqlite3.connect(self.db_path)

    def _init(self):
        with self._conn() as c:
            c.execute("""CREATE TABLE IF NOT EXISTS kv(
                namespace TEXT,
                k TEXT,
                v_json TEXT,
                updated_at TEXT,
                ttl_seconds INTEGER,
                PRIMARY KEY(namespace, k)
            )""")
            c.execute("""CREATE TABLE IF NOT EXISTS logs(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                namespace TEXT,
                record_json TEXT,
                created_at TEXT
            )""")
            c.commit()

    def read(self, namespace: str, key: str):
        with self._conn() as c:
            row = c.execute("SELECT v_json FROM kv WHERE namespace=? AND k=?", (namespace, key)).fetchone()
            if not row:
                return None
            return json.loads(row[0])

    def write(self, namespace: str, key: str, value, ttl: int | None = None):
        from kimaru_core.utils.time import utc_now_iso
        with self._conn() as c:
            c.execute("""INSERT INTO kv(namespace,k,v_json,updated_at,ttl_seconds) VALUES(?,?,?,?,?)
                         ON CONFLICT(namespace,k) DO UPDATE SET v_json=excluded.v_json, updated_at=excluded.updated_at, ttl_seconds=excluded.ttl_seconds""",
                      (namespace, key, json.dumps(value, ensure_ascii=False), utc_now_iso(), ttl))
            c.commit()

    def append_log(self, namespace: str, record):
        from kimaru_core.utils.time import utc_now_iso
        with self._conn() as c:
            c.execute("INSERT INTO logs(namespace, record_json, created_at) VALUES(?,?,?)",
                      (namespace, json.dumps(record, ensure_ascii=False), utc_now_iso()))
            c.commit()
