from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Literal, Optional

from kimaru_core.artifacts.artifact_ref import ArtifactRef

RunMode = Literal["full", "incremental", "validate_only"]
FederationScope = Literal["none", "metadata", "delta", "full"]
ZoneStatus = Literal["success", "blocked", "requires_approval", "failed"]

class ZoneRequest(BaseModel):
    session_id: str
    epoch_id: str
    run_mode: RunMode = "full"
    inputs: Dict[str, Any] = Field(default_factory=dict)

    intent_ref: Optional[ArtifactRef] = None
    scenario_ref: Optional[ArtifactRef] = None

    federation_scope: FederationScope = "none"
    requested_outputs: Optional[List[str]] = None

class PointerUpdate(BaseModel):
    pointer_key: str
    artifact_ref: ArtifactRef

class ZoneResult(BaseModel):
    status: ZoneStatus
    produced_artifacts: List[ArtifactRef] = Field(default_factory=list)
    updated_pointers: List[PointerUpdate] = Field(default_factory=list)
    produced_deltas: List[ArtifactRef] = Field(default_factory=list)

    events_summary: Dict[str, int] = Field(default_factory=dict)
    explain: str = ""
    errors: List[str] = Field(default_factory=list)
