from __future__ import annotations
import sqlite3
from typing import Optional, List, Tuple
from kimaru_core.artifacts.artifact_ref import ArtifactRef

class ActivePointerStore:
    def set_active(self, tenant_id: str, decision_context_id: str, pointer_key: str, artifact_ref: ArtifactRef, updated_at: str) -> None: ...
    def get_active(self, tenant_id: str, decision_context_id: str, pointer_key: str) -> Optional[ArtifactRef]: ...
    def list_active(self, tenant_id: str, decision_context_id: str, prefix: str | None = None) -> List[Tuple[str, ArtifactRef]]: ...

class SQLiteActivePointerStore(ActivePointerStore):
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init()

    def _conn(self):
        return sqlite3.connect(self.db_path)

    def _init(self):
        with self._conn() as c:
            c.execute("""CREATE TABLE IF NOT EXISTS pointers(
                tenant_id TEXT,
                decision_context_id TEXT,
                pointer_key TEXT,
                kind TEXT,
                artifact_id TEXT,
                updated_at TEXT,
                PRIMARY KEY (tenant_id, decision_context_id, pointer_key)
            )""")
            c.commit()

    def set_active(self, tenant_id: str, decision_context_id: str, pointer_key: str, artifact_ref: ArtifactRef, updated_at: str) -> None:
        with self._conn() as c:
            c.execute("""INSERT INTO pointers(tenant_id, decision_context_id, pointer_key, kind, artifact_id, updated_at)
                         VALUES(?,?,?,?,?,?)
                         ON CONFLICT(tenant_id, decision_context_id, pointer_key)
                         DO UPDATE SET kind=excluded.kind, artifact_id=excluded.artifact_id, updated_at=excluded.updated_at
                      """, (tenant_id, decision_context_id, pointer_key, artifact_ref.kind, artifact_ref.artifact_id, updated_at))
            c.commit()

    def get_active(self, tenant_id: str, decision_context_id: str, pointer_key: str) -> Optional[ArtifactRef]:
        with self._conn() as c:
            row = c.execute("""SELECT kind, artifact_id FROM pointers
                                 WHERE tenant_id=? AND decision_context_id=? AND pointer_key=?""",
                            (tenant_id, decision_context_id, pointer_key)).fetchone()
            if not row:
                return None
            return ArtifactRef(kind=row[0], artifact_id=row[1])

    def list_active(self, tenant_id: str, decision_context_id: str, prefix: str | None = None):
        q = "SELECT pointer_key, kind, artifact_id FROM pointers WHERE tenant_id=? AND decision_context_id=?"
        params = [tenant_id, decision_context_id]
        if prefix:
            q += " AND pointer_key LIKE ?"
            params.append(prefix + "%")
        with self._conn() as c:
            rows = c.execute(q, params).fetchall()
            return [(r[0], ArtifactRef(kind=r[1], artifact_id=r[2])) for r in rows]
