from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, Literal, List, Dict
from kimaru_core.utils.time import utc_now_iso

class TenantRef(BaseModel):
    tenant_id: str
    environment: str = "onprem"
    display_name: Optional[str] = None

class DecisionContextRef(BaseModel):
    decision_context_id: str
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

class ActorRef(BaseModel):
    actor_type: Literal["human","agent","system"] = "system"
    actor_id: str = "system"
    display_name: Optional[str] = None

class TraceContext(BaseModel):
    trace_id: str
    correlation_id: Optional[str] = None

class SessionContext(BaseModel):
    session_id: str
    tenant_id: str
    decision_context_id: str
    mode: Literal["live","whatif"] = "live"
    status: Literal["active","closed"] = "active"
    created_at: str = Field(default_factory=utc_now_iso)

class EpochContext(BaseModel):
    epoch_id: str
    session_id: str
    sequence_no: int
    trigger: Dict[str, str] = Field(default_factory=dict)
    created_at: str = Field(default_factory=utc_now_iso)
    derived_from_epoch_id: Optional[str] = None

class RunContext(BaseModel):
    run_id: str
    session_id: str
    epoch_id: str
    zone_id: str = "core"
    run_mode: Literal["auto","manual"] = "auto"
    created_at: str = Field(default_factory=utc_now_iso)
    kernel_version: str = "0.1.0"
    trace_id: str
    correlation_id: Optional[str] = None

class NodeRef(BaseModel):
    node_id: str
    org_id: Optional[str] = None
    site_id: Optional[str] = None
    network_zone: Literal["local","intra","external"] = "local"
    public_key: Optional[str] = None
    trust_level: Literal["low","medium","high"] = "medium"

class FederationContext(BaseModel):
    federation_id: Optional[str] = None
    node: NodeRef
    peers: List[NodeRef] = Field(default_factory=list)
    replication_mode: Literal["none","metadata","delta","full"] = "delta"
