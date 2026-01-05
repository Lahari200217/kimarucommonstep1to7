from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from kimaru_core.artifacts.artifact_ref import ArtifactRef
from kimaru_core.utils.time import utc_now_iso

class ProducerRef(BaseModel):
    name: str
    version: str

class ArtifactHeader(BaseModel):
    tenant_id: str
    decision_context_id: str
    session_id: str
    epoch_id: str
    run_id: str
    zone_id: str
    created_at: str = Field(default_factory=utc_now_iso)
    producer: ProducerRef
    inputs: List[ArtifactRef] = Field(default_factory=list)
    config_snapshot_ref: Optional[ArtifactRef] = None
    logical_version: Optional[int] = None
    tags: Dict[str, Any] = Field(default_factory=dict)

class IntegrityRecord(BaseModel):
    checksum_alg: str = "sha256"
    checksum: str
    status: str = "pass"
    errors: List[str] = Field(default_factory=list)

class ArtifactEnvelope(BaseModel):
    header: ArtifactHeader
    payload: Any
    integrity: IntegrityRecord
