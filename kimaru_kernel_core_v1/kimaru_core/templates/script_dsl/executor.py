from __future__ import annotations
from typing import Any, Dict, List
from kimaru_core.utils.ids import new_id
from kimaru_core.decision_tracker.models import TrackEvent
from kimaru_core.decision_tracker import event_types as ET
from kimaru_core.artifacts.artifact_ref import ArtifactRef
from kimaru_core.artifacts.artifact_models import ArtifactHeader, ArtifactEnvelope, IntegrityRecord, ProducerRef
from kimaru_core.artifacts.integrity import compute_envelope_checksum
from kimaru_core.utils.time import utc_now_iso

def exec_script(ctx, agent_desc, script: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
    state: Dict[str, Any] = {"inputs": inputs, "vars": {}, "outputs": {}}
    for step in script["steps"]:
        stype = step["type"]

        if stype == "algorithm":
            alg_id = step["algorithm_id"]
            version = step.get("version")
            alg = ctx.algorithms.resolve(alg_id, version)
            alg_inputs = _resolve_map(step.get("inputs", {}), state)
            # audit selection
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
                event_type="ALGORITHM_SELECTED",
                message=f"selected {alg_id}",
                refs={"algorithm_id": alg_id, "algorithm_version": getattr(alg.describe(), "version", None)},
                metadata={},
            ))
            result = alg.run(ctx, alg_inputs)
            var = step.get("save_as")
            if var:
                state["vars"][var] = result
            state["outputs"][step.get("output_key","last_algorithm")] = result

        elif stype == "store_artifact":
            kind = step["kind"]
            payload = _resolve_map(step.get("payload", {}), state)
            artifact_id = step.get("artifact_id") or new_id("a")
            ref = ArtifactRef(kind=kind, artifact_id=artifact_id)
            header = ArtifactHeader(
                tenant_id=ctx.tenant.tenant_id,
                decision_context_id=ctx.decision_context.decision_context_id,
                session_id=ctx.session.session_id,
                epoch_id=ctx.epoch.epoch_id,
                run_id=ctx.run.run_id,
                zone_id=ctx.run.zone_id,
                producer=ProducerRef(name=agent_desc.agent_type_id, version=agent_desc.version),
                inputs=[ArtifactRef.model_validate(x) for x in step.get("inputs", [])],
                logical_version=ctx.epoch.sequence_no,
                tags={"security_flag": str(agent_desc.security_flag)},
            )
            checksum = compute_envelope_checksum(header.model_dump(), payload)
            env = ArtifactEnvelope(header=header, payload=payload, integrity=IntegrityRecord(checksum=checksum))
            ctx.artifacts.put(ref, env)
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
                event_type=ET.ARTIFACT_STORED,
                message=f"stored artifact {ref.key()}",
                refs={"artifact_ref": ref.model_dump()},
                metadata={},
            ))
            state["vars"][step.get("save_as","artifact_ref")] = ref.model_dump()

        elif stype == "set_pointer":
            pointer_key = step["pointer_key"]
            aref = _resolve_value(step["artifact_ref"], state)
            ref = ArtifactRef.model_validate(aref)
            # governance gate for approved/active pointers is handled by GovernanceGateway
            ctx.governance.before_pointer_set(ctx, pointer_key, ref)
            ctx.pointers.set_active(ctx.tenant.tenant_id, ctx.decision_context.decision_context_id, pointer_key, ref, utc_now_iso())
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
                event_type=ET.POINTER_SET,
                message=f"pointer set {pointer_key} -> {ref.key()}",
                refs={"pointer_key": pointer_key, "artifact_ref": ref.model_dump()},
                metadata={},
            ))
            state["vars"][step.get("save_as","pointer_set")] = {"pointer_key": pointer_key, "artifact_ref": ref.model_dump()}

        elif stype == "memory_write":
            ns = step["namespace"]
            key = step["key"]
            val = _resolve_value(step["value"], state)
            ctx.memory.write(ns, key, val, ttl=step.get("ttl"))
            state["vars"][step.get("save_as","memory_write")] = {"namespace": ns, "key": key}

        elif stype == "memory_read":
            ns = step["namespace"]
            key = step["key"]
            val = ctx.memory.read(ns, key)
            state["vars"][step.get("save_as","memory_read")] = val

        else:
            raise ValueError(f"Unsupported step type: {stype}")

    return {"vars": state["vars"], "outputs": state["outputs"]}

def _resolve_value(v: Any, state: Dict[str, Any]) -> Any:
    # Supports references like ${vars.x} or ${inputs.rows}
    if isinstance(v, str) and v.startswith("${") and v.endswith("}"):
        path = v[2:-1].strip()
        parts = path.split(".")
        cur: Any = state
        for p in parts:
            if p not in cur:
                raise KeyError(f"Script reference missing: {path}")
            cur = cur[p]
        return cur
    return v

def _resolve_map(m: Any, state: Dict[str, Any]) -> Any:
    if isinstance(m, dict):
        return {k: _resolve_map(v, state) for k,v in m.items()}
    if isinstance(m, list):
        return [_resolve_map(x, state) for x in m]
    return _resolve_value(m, state)
