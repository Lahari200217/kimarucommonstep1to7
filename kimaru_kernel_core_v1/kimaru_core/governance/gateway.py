from __future__ import annotations
from typing import Any, Dict, Optional
from kimaru_core.governance.models import GovernanceDecision
from kimaru_core.agent_fabric.security_flag import SecurityFlag
from kimaru_core.artifacts.artifact_ref import ArtifactRef

class GovernanceGateway:
    # Core interface (Zone-5 plugs later). This default implementation is strict but simple.
    def pre_check(self, ctx, decision_intent: Optional[dict], execution_plan: Dict[str, Any]) -> Dict[str, Any]:
        agent = execution_plan.get("agent", {})
        security_flag = agent.get("security_flag")
        decision_class = agent.get("decision_class", "advisory")

        # Ethics baseline: executable decisions cannot use RED_EXTERNAL unless explicitly allowed by ctx + policy.
        if decision_class == "executable" and security_flag == SecurityFlag.RED_EXTERNAL:
            return {"decision": "BLOCK", "reason": "Ethics: executable decision cannot use RED_EXTERNAL agent"}

        return {"decision": "ALLOW"}

    def post_check(self, ctx, outcome_ref: Optional[ArtifactRef]) -> Dict[str, Any]:
        return {"decision": "ACCEPT"}

    def before_pointer_set(self, ctx, pointer_key: str, ref: ArtifactRef) -> None:
        # Enforce approvals for sensitive pointers.
        needs_approval = pointer_key.endswith("/approved") or pointer_key.endswith("/active")
        if not needs_approval:
            return
        # Only a human governor can set approved/active pointers in this v1.
        if ctx.actor.actor_type != "human" or ctx.actor.actor_id not in ("governor","admin"):
            raise PermissionError(f"Pointer update requires human approval role for {pointer_key}")
