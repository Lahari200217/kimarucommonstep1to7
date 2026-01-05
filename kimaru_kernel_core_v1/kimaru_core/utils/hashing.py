from __future__ import annotations
import hashlib
import json
from typing import Any

def sha256_bytes(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()

def canonical_json_dumps(obj: Any) -> str:
    # Deterministic JSON: sorted keys, no whitespace.
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def sha256_canonical_json(obj: Any) -> str:
    return sha256_bytes(canonical_json_dumps(obj).encode("utf-8"))
