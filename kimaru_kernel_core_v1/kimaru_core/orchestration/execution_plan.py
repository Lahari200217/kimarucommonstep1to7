from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Dict

from kimaru_core.agent_fabric.security_flag import SecurityFlag

FederationAction = Literal["none", "publish_delta", "request_remote_sim", "browse_remote", "pointer_sync"]

class ExecutionPlan(BaseModel):
    """A declarative plan of what a ZoneKernel intends to do.

    Governance uses this to allow/block/require-approval.
    The plan must be truthful; Core logs it for audit.
    """
    zone_id: str
    agents_to_invoke: List[Dict[str, str]] = Field(default_factory=list)  # {agent_type_id, version}
    capabilities: List[str] = Field(default_factory=list)
    algorithms_expected: List[Dict[str, str]] = Field(default_factory=list)  # {algorithm_id, version}
    artifact_kinds_to_produce: List[str] = Field(default_factory=list)
    pointer_keys_may_update: List[str] = Field(default_factory=list)
    federation_actions: List[FederationAction] = Field(default_factory=list)
    security_flags_involved: List[SecurityFlag] = Field(default_factory=list)

    notes: Optional[str] = None
