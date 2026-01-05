from __future__ import annotations
from typing import Any, Dict, List
from kimaru_core.utils.validation import require_keys

def validate_script(script: Dict[str, Any]) -> None:
    require_keys(script, ["script_id","language","steps"], "agent_script")
    if script["language"] != "kimaruscript.v1":
        raise ValueError("Unsupported script language")
    if not isinstance(script["steps"], list) or not script["steps"]:
        raise ValueError("script.steps must be a non-empty list")
    for i, step in enumerate(script["steps"]):
        require_keys(step, ["type"], f"step[{i}]")
