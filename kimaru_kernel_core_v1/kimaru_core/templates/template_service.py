from __future__ import annotations
from typing import Any, Dict, Optional, List
from kimaru_core.artifacts.artifact_ref import ArtifactRef
from kimaru_core.artifacts.artifact_models import ArtifactHeader, ArtifactEnvelope, IntegrityRecord, ProducerRef
from kimaru_core.artifacts.integrity import compute_envelope_checksum
from kimaru_core.utils.ids import new_id
from kimaru_core.utils.time import utc_now_iso
from kimaru_core.decision_tracker.models import TrackEvent
from kimaru_core.decision_tracker import event_types as ET

class TemplateService:
    def __init__(self, artifacts, pointers, tracker):
        self.artifacts = artifacts
        self.pointers = pointers
        self.tracker = tracker

    def put(self, ctx, kind: str, payload: Dict[str, Any], pointer_key: Optional[str] = None, tags: Optional[Dict[str, Any]] = None) -> ArtifactRef:
        ref = ArtifactRef(kind=kind, artifact_id=new_id("tpl"))
        header = ArtifactHeader(
            tenant_id=ctx.tenant.tenant_id,
            decision_context_id=ctx.decision_context.decision_context_id,
            session_id=ctx.session.session_id,
            epoch_id=ctx.epoch.epoch_id,
            run_id=ctx.run.run_id,
            zone_id=ctx.run.zone_id,
            producer=ProducerRef(name="template_service", version="1.0.0"),
            inputs=[],
            logical_version=ctx.epoch.sequence_no,
            tags=tags or {},
        )
        checksum = compute_envelope_checksum(header.model_dump(), payload)
        env = ArtifactEnvelope(header=header, payload=payload, integrity=IntegrityRecord(checksum=checksum))
        self.artifacts.put(ref, env)
        self.tracker.append(TrackEvent(
            event_id=new_id("ev"),
            tenant_id=ctx.tenant.tenant_id,
            decision_context_id=ctx.decision_context.decision_context_id,
            session_id=ctx.session.session_id,
            epoch_id=ctx.epoch.epoch_id,
            run_id=ctx.run.run_id,
            zone_id=ctx.run.zone_id,
            event_type=ET.ARTIFACT_STORED,
            message=f"stored template {ref.key()}",
            refs={"artifact_ref": ref.model_dump()},
            metadata={},
        ))
        if pointer_key:
            ctx.governance.before_pointer_set(ctx, pointer_key, ref)
            self.pointers.set_active(ctx.tenant.tenant_id, ctx.decision_context.decision_context_id, pointer_key, ref, utc_now_iso())
        return ref
