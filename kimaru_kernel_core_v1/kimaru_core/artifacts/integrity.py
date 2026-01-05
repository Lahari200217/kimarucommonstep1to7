from __future__ import annotations
from typing import Any, Dict
from kimaru_core.utils.hashing import sha256_canonical_json, canonical_json_dumps

def compute_envelope_checksum(header: Dict[str, Any], payload: Any) -> str:
    # Integrity covers header+payload deterministically
    obj = {"header": header, "payload": payload}
    return sha256_canonical_json(obj)
