from __future__ import annotations
from typing import Any, Dict

def require_keys(obj: Dict[str, Any], keys: list[str], what: str) -> None:
    missing = [k for k in keys if k not in obj]
    if missing:
        raise ValueError(f"{what} missing keys: {missing}")
