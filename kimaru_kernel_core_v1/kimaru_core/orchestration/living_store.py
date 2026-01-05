from __future__ import annotations
import sqlite3
from typing import Optional, List
from kimaru_core.identity.models import SessionContext, EpochContext, RunContext
from kimaru_core.utils.time import utc_now_iso

class LivingStore:
    def create_session(self, session: SessionContext) -> None: ...
    def get_session(self, session_id: str) -> SessionContext: ...
    def list_sessions(self, tenant_id: str, decision_context_id: str, limit: int=50) -> List[SessionContext]: ...
    def create_epoch(self, epoch: EpochContext) -> None: ...
    def list_epochs(self, session_id: str) -> List[EpochContext]: ...
    def create_run(self, run: RunContext) -> None: ...
    def list_runs(self, session_id: str, limit: int=100) -> List[RunContext]: ...

class SQLiteLivingStore(LivingStore):
    def __init__(self, db_path: str):
        self.db_path=db_path
        self._init()
    def _conn(self):
        return sqlite3.connect(self.db_path)
    def _init(self):
        with self._conn() as c:
            c.execute("""CREATE TABLE IF NOT EXISTS sessions(
                session_id TEXT PRIMARY KEY,
                tenant_id TEXT,
                decision_context_id TEXT,
                mode TEXT,
                status TEXT,
                created_at TEXT
            )""")
            c.execute("""CREATE TABLE IF NOT EXISTS epochs(
                epoch_id TEXT PRIMARY KEY,
                session_id TEXT,
                sequence_no INTEGER,
                trigger_json TEXT,
                created_at TEXT,
                derived_from_epoch_id TEXT
            )""")
            c.execute("""CREATE TABLE IF NOT EXISTS runs(
                run_id TEXT PRIMARY KEY,
                session_id TEXT,
                epoch_id TEXT,
                zone_id TEXT,
                run_mode TEXT,
                created_at TEXT,
                kernel_version TEXT,
                trace_id TEXT,
                correlation_id TEXT
            )""")
            c.commit()
    def create_session(self, session: SessionContext) -> None:
        with self._conn() as c:
            c.execute("INSERT INTO sessions VALUES(?,?,?,?,?,?)",
                      (session.session_id, session.tenant_id, session.decision_context_id, session.mode, session.status, session.created_at))
            c.commit()
    def get_session(self, session_id: str) -> SessionContext:
        with self._conn() as c:
            r=c.execute("SELECT session_id,tenant_id,decision_context_id,mode,status,created_at FROM sessions WHERE session_id=?",(session_id,)).fetchone()
        if not r: raise KeyError("session not found")
        return SessionContext(session_id=r[0], tenant_id=r[1], decision_context_id=r[2], mode=r[3], status=r[4], created_at=r[5])
    def list_sessions(self, tenant_id: str, decision_context_id: str, limit: int=50):
        with self._conn() as c:
            rows=c.execute("SELECT session_id,tenant_id,decision_context_id,mode,status,created_at FROM sessions WHERE tenant_id=? AND decision_context_id=? ORDER BY created_at DESC LIMIT ?",
                           (tenant_id, decision_context_id, limit)).fetchall()
        return [SessionContext(session_id=r[0], tenant_id=r[1], decision_context_id=r[2], mode=r[3], status=r[4], created_at=r[5]) for r in rows]
    def create_epoch(self, epoch: EpochContext) -> None:
        import json
        with self._conn() as c:
            c.execute("INSERT INTO epochs VALUES(?,?,?,?,?,?)",
                      (epoch.epoch_id, epoch.session_id, epoch.sequence_no, json.dumps(epoch.trigger, ensure_ascii=False), epoch.created_at, epoch.derived_from_epoch_id))
            c.commit()
    def list_epochs(self, session_id: str):
        import json
        with self._conn() as c:
            rows=c.execute("SELECT epoch_id,session_id,sequence_no,trigger_json,created_at,derived_from_epoch_id FROM epochs WHERE session_id=? ORDER BY sequence_no ASC",(session_id,)).fetchall()
        return [EpochContext(epoch_id=r[0], session_id=r[1], sequence_no=r[2], trigger=json.loads(r[3]) if r[3] else {}, created_at=r[4], derived_from_epoch_id=r[5]) for r in rows]
    def create_run(self, run: RunContext) -> None:
        with self._conn() as c:
            c.execute("INSERT INTO runs VALUES(?,?,?,?,?,?,?,?,?)",
                      (run.run_id, run.session_id, run.epoch_id, run.zone_id, run.run_mode, run.created_at, run.kernel_version, run.trace_id, run.correlation_id))
            c.commit()
    def list_runs(self, session_id: str, limit: int=100):
        with self._conn() as c:
            rows=c.execute("SELECT run_id,session_id,epoch_id,zone_id,run_mode,created_at,kernel_version,trace_id,correlation_id FROM runs WHERE session_id=? ORDER BY created_at DESC LIMIT ?",
                           (session_id, limit)).fetchall()
        return [RunContext(run_id=r[0], session_id=r[1], epoch_id=r[2], zone_id=r[3], run_mode=r[4], created_at=r[5], kernel_version=r[6], trace_id=r[7], correlation_id=r[8]) for r in rows]
