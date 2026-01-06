from __future__ import annotations
import os
from pathlib import Path
from typing import Any, Dict, Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel

from kimaru_core.utils.ids import new_id
from kimaru_core.utils.time import utc_now_iso

from kimaru_core.identity.models import TenantRef, DecisionContextRef, ActorRef, TraceContext, SessionContext, EpochContext, RunContext, NodeRef, FederationContext
from kimaru_core.core_context import CoreContext
from kimaru_core.artifacts.artifact_store import FileSystemArtifactStore
from kimaru_core.artifacts.active_pointer_store import SQLiteActivePointerStore
from kimaru_core.decision_tracker import SQLiteDecisionTracker
from kimaru_core.agent_fabric import AgentRegistry, PolicyGuard, ObserveStream
from kimaru_core.agent_fabric.invoker import CapabilityInvoker
from kimaru_core.governance import GovernanceGateway
from kimaru_core.memory import SQLiteAgentMemory
from kimaru_core.algorithms import AlgorithmRegistry
from kimaru_core.algorithms.generic.data_cleaning import BasicCleaner
from kimaru_core.orchestration import SQLiteLivingStore
from kimaru_core.templates import TemplateService
from kimaru_core.artifacts.artifact_ref import ArtifactRef
from kimaru_core.agent_fabric.descriptor import AgentDescriptor
from kimaru_core.agent_fabric.security_flag import SecurityFlag
from kimaru_core.agent_fabric.scripted_agent import ScriptedAgentFactory

BASE_DIR = Path(os.getenv("KIMARU_VAR_DIR", Path.cwd() / "var"))
ART_DIR = BASE_DIR / "artifacts"
DB_DIR = BASE_DIR / "db"
DB_DIR.mkdir(parents=True, exist_ok=True)
ART_DIR.mkdir(parents=True, exist_ok=True)

artifact_store = FileSystemArtifactStore(str(ART_DIR))
pointer_store = SQLiteActivePointerStore(str(DB_DIR / "pointers.sqlite"))
tracker = SQLiteDecisionTracker(str(DB_DIR / "tracker.sqlite"))
memory = SQLiteAgentMemory(str(DB_DIR / "memory.sqlite"))
living = SQLiteLivingStore(str(DB_DIR / "living.sqlite"))

agents = AgentRegistry()
algorithms = AlgorithmRegistry()
algorithms.register(BasicCleaner())

policy = PolicyGuard()
governance = GovernanceGateway()
observe = ObserveStream()
invoker = CapabilityInvoker()
templates = TemplateService(artifact_store, pointer_store, tracker)

# Simple in-memory realtime buffer for SSE
_realtime: List[dict] = []
def _obs(event_type: str, payload: dict):
    payload = {"ts": utc_now_iso(), "type": event_type, "payload": payload}
    _realtime.append(payload)
    del _realtime[:-2000]  # keep last N

observe.subscribe(_obs)

app = FastAPI(title="Kimaru Kernel Common Core Demo", version="0.1.0")

# Register v1 API routers
from kimaru_core.app.api.v1 import manifest as manifest_v1
app.include_router(manifest_v1.router)

DEFAULT_TENANT = TenantRef(tenant_id="tenant_demo", display_name="Demo Tenant")
DEFAULT_DCTX = DecisionContextRef(decision_context_id="decision_demo", description="Demo decision context")
DEFAULT_NODE = NodeRef(node_id="node_local", network_zone="local", trust_level="high")
DEFAULT_FED = FederationContext(federation_id="fed_demo", node=DEFAULT_NODE, peers=[], replication_mode="delta")

def make_ctx(session: SessionContext, epoch: EpochContext, run: RunContext, actor: ActorRef) -> CoreContext:
    return CoreContext(
        tenant=DEFAULT_TENANT,
        decision_context=DEFAULT_DCTX,
        session=session,
        epoch=epoch,
        run=run,
        actor=actor,
        trace=TraceContext(trace_id=run.trace_id, correlation_id=run.correlation_id),
        federation=DEFAULT_FED,
        artifacts=artifact_store,
        pointers=pointer_store,
        tracker=tracker,
        agents=agents,
        algorithms=algorithms,
        policy=policy,
        governance=governance,
        observe=observe,
        memory=memory,
        allow_external=False,
        debug=True,
    )

class CreateSessionReq(BaseModel):
    mode: str = "live"

@app.post("/api/sessions")
def create_session(req: CreateSessionReq):
    sid = new_id("sess")
    session = SessionContext(session_id=sid, tenant_id=DEFAULT_TENANT.tenant_id, decision_context_id=DEFAULT_DCTX.decision_context_id, mode=req.mode)
    living.create_session(session)
    return session.model_dump()

@app.get("/api/sessions")
def list_sessions(limit: int = 50):
    items = living.list_sessions(DEFAULT_TENANT.tenant_id, DEFAULT_DCTX.decision_context_id, limit=limit)
    return [s.model_dump() for s in items]

class CreateEpochReq(BaseModel):
    trigger: Dict[str, str] = {}

@app.post("/api/sessions/{session_id}/epochs")
def create_epoch(session_id: str, req: CreateEpochReq):
    session = living.get_session(session_id)
    epochs = living.list_epochs(session_id)
    seq = (epochs[-1].sequence_no + 1) if epochs else 1
    epoch = EpochContext(epoch_id=new_id("epoch"), session_id=session_id, sequence_no=seq, trigger=req.trigger)
    living.create_epoch(epoch)
    return epoch.model_dump()

@app.get("/api/sessions/{session_id}/epochs")
def list_epochs(session_id: str):
    return [e.model_dump() for e in living.list_epochs(session_id)]

@app.get("/api/sessions/{session_id}/runs")
def list_runs(session_id: str, limit: int = 100):
    return [r.model_dump() for r in living.list_runs(session_id, limit=limit)]

class PutScriptReq(BaseModel):
    script: Dict[str, Any]
    pointer_key: Optional[str] = None

@app.post("/api/scripts")
def put_script(req: PutScriptReq):
    # store as artifact kind agent_script
    # needs a session/epoch/run context; make ephemeral system run
    session = SessionContext(session_id=new_id("sess"), tenant_id=DEFAULT_TENANT.tenant_id, decision_context_id=DEFAULT_DCTX.decision_context_id)
    living.create_session(session)
    epoch = EpochContext(epoch_id=new_id("epoch"), session_id=session.session_id, sequence_no=1, trigger={"type":"script_upload"})
    living.create_epoch(epoch)
    run = RunContext(run_id=new_id("run"), session_id=session.session_id, epoch_id=epoch.epoch_id, zone_id="core", trace_id=new_id("trace"))
    living.create_run(run)
    ctx = make_ctx(session, epoch, run, ActorRef(actor_type="human", actor_id="admin", display_name="admin"))
    ref = templates.put(ctx, kind="agent_script", payload=req.script, pointer_key=req.pointer_key)
    return ref.model_dump()

class RegisterScriptedAgentReq(BaseModel):
    agent_type_id: str
    version: str = "1.0.0"
    security_flag: str = "GREEN"
    script_ref: ArtifactRef
    zone_id: str = "core"

@app.post("/api/agents/register_scripted")
def register_scripted(req: RegisterScriptedAgentReq):
    sf = SecurityFlag.GREEN_INTERNAL if req.security_flag.upper().startswith("G") else (SecurityFlag.YELLOW_INTRA if req.security_flag.upper().startswith("Y") else SecurityFlag.RED_EXTERNAL)
    desc = AgentDescriptor(
        agent_type_id=req.agent_type_id,
        version=req.version,
        zone_id=req.zone_id,
        security_flag=sf,
        capabilities=["run"],
        inputs_schema={"type":"object"},
        outputs_schema={"type":"object"},
    )
    factory = ScriptedAgentFactory(desc, req.script_ref)
    agents.register(desc, factory)
    return {"status":"ok", "agent": desc.model_dump()}

class RunAgentReq(BaseModel):
    session_id: str
    epoch_id: str
    agent_type_id: str
    inputs: Dict[str, Any] = {}
    actor_id: str = "operator"

@app.post("/api/agents/run")
def run_agent(req: RunAgentReq):
    session = living.get_session(req.session_id)
    epochs = {e.epoch_id: e for e in living.list_epochs(req.session_id)}
    if req.epoch_id not in epochs:
        raise HTTPException(404, "epoch not found")
    epoch = epochs[req.epoch_id]
    run = RunContext(run_id=new_id("run"), session_id=session.session_id, epoch_id=epoch.epoch_id, zone_id="core", trace_id=new_id("trace"))
    living.create_run(run)
    actor = ActorRef(actor_type="human", actor_id=req.actor_id, display_name=req.actor_id)
    ctx = make_ctx(session, epoch, run, actor)

    desc, factory = agents.resolve(req.agent_type_id)
    agent = factory.create({}, ctx)
    out = invoker.invoke(ctx, desc, agent, "run", req.inputs)
    return {"run": run.model_dump(), "output": out}

@app.get("/api/agents")
def list_agents():
    return [a.model_dump() for a in agents.list()]

@app.get("/api/artifacts/{kind}/{artifact_id}")
def get_artifact(kind: str, artifact_id: str):
    ref = ArtifactRef(kind=kind, artifact_id=artifact_id)
    env = artifact_store.get(ref)
    return env.model_dump()

@app.get("/api/artifacts/{kind}")
def list_artifacts(kind: str, limit: int = 50):
    return [r.model_dump() for r in artifact_store.list(kind, limit=limit)]

@app.get("/api/pointers")
def list_pointers(prefix: Optional[str] = None):
    items = pointer_store.list_active(DEFAULT_TENANT.tenant_id, DEFAULT_DCTX.decision_context_id, prefix=prefix)
    return [{"pointer_key": k, "artifact_ref": v.model_dump()} for k,v in items]

@app.get("/api/events/{session_id}")
def get_events(session_id: str, limit: int = 200):
    return [e.model_dump() for e in tracker.query(session_id, limit=limit)]

@app.get("/api/realtime")
def realtime():
    def gen():
        # naive SSE from in-memory buffer
        idx = 0
        while True:
            while idx < len(_realtime):
                item = _realtime[idx]
                idx += 1
                yield f"data: {item}\n\n"
            import time
            time.sleep(0.4)
    return StreamingResponse(gen(), media_type="text/event-stream")

@app.get("/ui", response_class=HTMLResponse)
def ui():
    return HTMLResponse((Path(__file__).parent / "ui.html").read_text(encoding="utf-8"))

def main():
    import uvicorn
    uvicorn.run("kimaru_core.app.main:app", host="127.0.0.1", port=8000, reload=False)
