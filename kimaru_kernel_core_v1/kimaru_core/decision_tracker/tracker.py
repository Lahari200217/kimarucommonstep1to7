from __future__ import annotations
import sqlite3, json
from typing import List, Optional, Dict, Any
from kimaru_core.decision_tracker.models import TrackEvent

class QuerySpec(dict):
    pass

class DecisionTracker:
    def append(self, event: TrackEvent) -> None: ...
    def query(self, session_id: str, limit: int = 200, event_type: str | None = None) -> List[TrackEvent]: ...

class SQLiteDecisionTracker(DecisionTracker):
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init()

    def _conn(self):
        return sqlite3.connect(self.db_path)

    def _init(self):
        with self._conn() as c:
            c.execute("""CREATE TABLE IF NOT EXISTS events(
                event_id TEXT PRIMARY KEY,
                created_at TEXT,
                tenant_id TEXT,
                decision_context_id TEXT,
                session_id TEXT,
                epoch_id TEXT,
                run_id TEXT,
                zone_id TEXT,
                actor_type TEXT,
                actor_id TEXT,
                actor_display_name TEXT,
                event_type TEXT,
                severity TEXT,
                message TEXT,
                refs_json TEXT,
                metadata_json TEXT
            )""")
            c.execute("CREATE INDEX IF NOT EXISTS idx_events_session ON events(session_id, created_at)")
            c.execute("CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type, created_at)")
            c.commit()

    def append(self, event: TrackEvent) -> None:
        with self._conn() as c:
            c.execute("""INSERT INTO events VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (
                event.event_id, event.created_at,
                event.tenant_id, event.decision_context_id, event.session_id, event.epoch_id, event.run_id, event.zone_id,
                event.actor_type, event.actor_id, event.actor_display_name,
                event.event_type, event.severity, event.message,
                json.dumps(event.refs, ensure_ascii=False),
                json.dumps(event.metadata, ensure_ascii=False),
            ))
            c.commit()

    def query(self, session_id: str, limit: int = 200, event_type: str | None = None) -> List[TrackEvent]:
        q = "SELECT * FROM events WHERE session_id=?"
        params = [session_id]
        if event_type:
            q += " AND event_type=?"
            params.append(event_type)
        q += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        with self._conn() as c:
            rows = c.execute(q, params).fetchall()
        events = []
        for r in rows:
            events.append(TrackEvent(
                event_id=r[0], created_at=r[1],
                tenant_id=r[2], decision_context_id=r[3], session_id=r[4], epoch_id=r[5], run_id=r[6], zone_id=r[7],
                actor_type=r[8], actor_id=r[9], actor_display_name=r[10],
                event_type=r[11], severity=r[12], message=r[13],
                refs=json.loads(r[14]) if r[14] else {},
                metadata=json.loads(r[15]) if r[15] else {},
            ))
        return events
