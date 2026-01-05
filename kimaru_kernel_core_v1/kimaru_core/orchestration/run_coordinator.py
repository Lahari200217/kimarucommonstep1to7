from __future__ import annotations
from typing import Dict, Optional

from kimaru_core.core_context import CoreContext
from kimaru_core.decision_tracker import event_types
from kimaru_core.decision_tracker.models import TrackEvent
from kimaru_core.utils.time import utc_now_iso
from kimaru_core.utils.ids import new_id
from kimaru_core.orchestration.zone_models import ZoneRequest, ZoneResult
from kimaru_core.orchestration.zone_kernel_interface import ZoneKernel

class RunCoordinator:
    """Core-owned router that executes a ZoneKernel with standard lifecycle events."""

    def __init__(self, zones: Dict[str, ZoneKernel]):
        self.zones = zones

    def run_zone(self, ctx: CoreContext, zone_id: str, request: ZoneRequest) -> ZoneResult:
        if zone_id not in self.zones:
            raise ValueError(f"ZoneKernel '{zone_id}' not loaded")

        # Update run_id for this execution if missing or placeholder
        if not getattr(ctx.run, "run_id", None):
            ctx.run.run_id = new_id("run")  # type: ignore[attr-defined]

        ctx.tracker.append(TrackEvent(
            event_id=new_id("evt"),
            created_at=utc_now_iso(),
            tenant_id=ctx.tenant.tenant_id,
            decision_context_id=ctx.decision_context.decision_context_id,
            session_id=ctx.session.session_id,
            epoch_id=ctx.epoch.epoch_id,
            run_id=ctx.run.run_id,
            zone_id=zone_id,
            actor_type=ctx.actor.actor_type,
            actor_id=ctx.actor.actor_id,
            event_type=event_types.RUN_STARTED,
            severity="INFO",
            message=f"Run started for {zone_id}",
            refs={"zone_id": zone_id},
            metadata={"run_mode": request.run_mode},
        ))
        ctx.observe.emit(event_types.RUN_STARTED, {"zone_id": zone_id, "session_id": ctx.session.session_id, "epoch_id": ctx.epoch.epoch_id, "run_id": ctx.run.run_id})

        try:
            result = self.zones[zone_id].execute(ctx, request)
            ctx.tracker.append(TrackEvent(
                event_id=new_id("evt"),
                created_at=utc_now_iso(),
                tenant_id=ctx.tenant.tenant_id,
                decision_context_id=ctx.decision_context.decision_context_id,
                session_id=ctx.session.session_id,
                epoch_id=ctx.epoch.epoch_id,
                run_id=ctx.run.run_id,
                zone_id=zone_id,
                actor_type=ctx.actor.actor_type,
                actor_id=ctx.actor.actor_id,
                event_type=event_types.RUN_ENDED if result.status == "success" else event_types.RUN_FAILED,
                severity="INFO" if result.status == "success" else "ERROR",
                message=f"Run ended for {zone_id} with status={result.status}",
                refs={"zone_id": zone_id},
                metadata={"status": result.status, "produced_artifacts": [r.model_dump() for r in result.produced_artifacts]},
            ))
            ctx.observe.emit(event_types.RUN_ENDED, {"zone_id": zone_id, "status": result.status, "run_id": ctx.run.run_id})
            return result
        except Exception as e:
            ctx.tracker.append(TrackEvent(
                event_id=new_id("evt"),
                created_at=utc_now_iso(),
                tenant_id=ctx.tenant.tenant_id,
                decision_context_id=ctx.decision_context.decision_context_id,
                session_id=ctx.session.session_id,
                epoch_id=ctx.epoch.epoch_id,
                run_id=ctx.run.run_id,
                zone_id=zone_id,
                actor_type=ctx.actor.actor_type,
                actor_id=ctx.actor.actor_id,
                event_type=event_types.RUN_FAILED,
                severity="CRITICAL",
                message=f"Run failed for {zone_id}: {e}",
                refs={"zone_id": zone_id},
                metadata={"exception": repr(e)},
            ))
            ctx.observe.emit(event_types.RUN_FAILED, {"zone_id": zone_id, "error": str(e), "run_id": ctx.run.run_id})
            raise
