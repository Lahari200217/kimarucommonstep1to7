from __future__ import annotations
from typing import List, Tuple, Dict, Any
from kimaru_core.agent_fabric.security_flag import SecurityFlag

class PolicyGuard:
    def allow(self, ctx, agent_desc, capability: str, resources: List[Dict[str, Any]] | None = None) -> Tuple[bool, List[str]]:
        resources = resources or []
        reasons = []
        # External safety rule
        if agent_desc.security_flag == SecurityFlag.RED_EXTERNAL and not ctx.allow_external:
            reasons.append("RED_EXTERNAL agent blocked: ctx.allow_external is False")
            return False, reasons
        return True, reasons
