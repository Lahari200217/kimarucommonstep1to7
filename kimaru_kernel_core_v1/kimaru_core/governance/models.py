from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any
from kimaru_core.utils.time import utc_now_iso
from kimaru_core.artifacts.artifact_ref import ArtifactRef

class DecisionIntent(BaseModel):
    intent_id: str
    decision_type: Literal["simulation","recommendation","execution"] = "recommendation"
    decision_class: Literal["informational","advisory","executable"] = "advisory"
    purpose: str
    risk_level: Literal["low","medium","high","critical"] = "low"
    zones_involved: List[str] = Field(default_factory=list)
    federation_scope: Literal["none","metadata","delta","full"] = "none"
    learning_effect: Literal["none","param_update","model_shift"] = "none"
    created_at: str = Field(default_factory=utc_now_iso)

class GovernanceDecision(BaseModel):
    decision: Literal["ALLOW","BLOCK","REQUIRE_APPROVAL"]
    reason: str = ""
    required_roles: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ApprovalRecord(BaseModel):
    approval_id: str
    decision_intent_ref: Optional[ArtifactRef] = None
    outcome_ref: Optional[ArtifactRef] = None
    approved_by: str
    approved_at: str = Field(default_factory=utc_now_iso)
    justification: str
    status: Literal["granted","rejected"] = "granted"
