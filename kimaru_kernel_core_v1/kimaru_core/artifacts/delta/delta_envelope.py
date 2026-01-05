from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Any, List, Literal, Optional, Dict
from kimaru_core.artifacts.artifact_ref import ArtifactRef

class DeltaOperation(BaseModel):
    op_type: Literal["json_patch","append_events","replace_section","param_delta","pointer_move"]
    data: Any

class DeltaEnvelope(BaseModel):
    delta_id: str
    delta_type: Literal["patch","event_log","param_update","pointer_update"] = "patch"
    base_ref: ArtifactRef
    target_kind: str
    apply_order: int
    hash_chain_prev: Optional[str] = None
    conflict_policy: Literal["reject","lww","merge"] = "reject"
    operations: List[DeltaOperation] = Field(default_factory=list)
    summary: str = ""
    created_by: str = ""
    extra: Dict[str, Any] = Field(default_factory=dict)
