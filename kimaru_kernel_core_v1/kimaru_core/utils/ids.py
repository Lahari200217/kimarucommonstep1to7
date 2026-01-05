from __future__ import annotations
import uuid

def new_id(prefix: str | None = None) -> str:
    u = uuid.uuid4().hex
    return f"{prefix}_{u}" if prefix else u
