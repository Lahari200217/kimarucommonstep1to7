from __future__ import annotations
from typing import Dict, Any, List, Optional
from kimaru_core.decision_tracker.models import TrackEvent
from kimaru_core.decision_tracker import event_types as ET
from kimaru_core.utils.ids import new_id

class CapabilityInvoker:
    def invoke(self, ctx, agent_desc, agent_instance, capability: str, inputs: Dict[str, Any], resources: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        # 1) Policy
        ok, reasons = ctx.policy.allow(ctx, agent_desc, capability, resources or [])
        ctx.tracker.append(TrackEvent(
            event_id=new_id("ev"),
            tenant_id=ctx.tenant.tenant_id,
            decision_context_id=ctx.decision_context.decision_context_id,
            session_id=ctx.session.session_id,
            epoch_id=ctx.epoch.epoch_id,
            run_id=ctx.run.run_id,
            zone_id=ctx.run.zone_id,
            actor_type=ctx.actor.actor_type,
            actor_id=ctx.actor.actor_id,
            actor_display_name=ctx.actor.display_name,
            event_type=ET.POLICY_ALLOW if ok else ET.POLICY_DENY,
            severity="INFO" if ok else "WARN",
            message="policy allow" if ok else "policy deny",
            refs={"agent_type_id": agent_desc.agent_type_id, "agent_version": agent_desc.version, "capability": capability},
            metadata={"reasons": reasons},
        ))
        if not ok:
            raise PermissionError("; ".join(reasons))

        # 2) Governance pre-check
        gov = ctx.governance.pre_check(ctx, decision_intent=None, execution_plan={"agent": agent_desc.model_dump(), "capability": capability})
        if gov["decision"] == "BLOCK":
            raise PermissionError("Governance blocked execution: " + gov.get("reason",""))
        if gov["decision"] == "REQUIRE_APPROVAL":
            raise PermissionError("Governance requires approval: " + gov.get("reason",""))

        # 3) Agent start
        ctx.tracker.append(TrackEvent(
            event_id=new_id("ev"),
            tenant_id=ctx.tenant.tenant_id,
            decision_context_id=ctx.decision_context.decision_context_id,
            session_id=ctx.session.session_id,
            epoch_id=ctx.epoch.epoch_id,
            run_id=ctx.run.run_id,
            zone_id=ctx.run.zone_id,
            actor_type="agent",
            actor_id=agent_desc.agent_type_id,
            actor_display_name=agent_desc.agent_type_id,
            event_type=ET.AGENT_START,
            message="agent start",
            refs={"agent_type_id": agent_desc.agent_type_id, "agent_version": agent_desc.version, "capability": capability},
            metadata={},
        ))
        ctx.observe.emit("AGENT_START", {"agent_type_id": agent_desc.agent_type_id, "run_id": ctx.run.run_id})

        try:
            out = agent_instance.run(ctx, inputs)
            ctx.tracker.append(TrackEvent(
                event_id=new_id("ev"),
                tenant_id=ctx.tenant.tenant_id,
                decision_context_id=ctx.decision_context.decision_context_id,
                session_id=ctx.session.session_id,
                epoch_id=ctx.epoch.epoch_id,
                run_id=ctx.run.run_id,
                zone_id=ctx.run.zone_id,
                actor_type="agent",
                actor_id=agent_desc.agent_type_id,
                actor_display_name=agent_desc.agent_type_id,
                event_type=ET.AGENT_END,
                message="agent end",
                refs={"agent_type_id": agent_desc.agent_type_id, "agent_version": agent_desc.version},
                metadata={},
            ))
            ctx.observe.emit("AGENT_END", {"agent_type_id": agent_desc.agent_type_id, "run_id": ctx.run.run_id})
        except Exception as e:
            ctx.tracker.append(TrackEvent(
                event_id=new_id("ev"),
                tenant_id=ctx.tenant.tenant_id,
                decision_context_id=ctx.decision_context.decision_context_id,
                session_id=ctx.session.session_id,
                epoch_id=ctx.epoch.epoch_id,
                run_id=ctx.run.run_id,
                zone_id=ctx.run.zone_id,
                actor_type="agent",
                actor_id=agent_desc.agent_type_id,
                actor_display_name=agent_desc.agent_type_id,
                event_type=ET.AGENT_FAIL,
                severity="ERROR",
                message=str(e),
                refs={"agent_type_id": agent_desc.agent_type_id, "agent_version": agent_desc.version},
                metadata={},
            ))
            ctx.observe.emit("AGENT_FAIL", {"agent_type_id": agent_desc.agent_type_id, "run_id": ctx.run.run_id, "error": str(e)})
            raise

        # 4) Governance post-check (optional in v1)
        ctx.governance.post_check(ctx, outcome_ref=None)
        return out
