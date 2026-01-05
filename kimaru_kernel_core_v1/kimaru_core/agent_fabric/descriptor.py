from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from kimaru_core.agent_fabric.security_flag import SecurityFlag

class AgentDescriptor(BaseModel):
    agent_type_id: str
    version: str = "1.0.0"
    zone_id: str = "core"
    security_flag: SecurityFlag = SecurityFlag.GREEN_INTERNAL
    capabilities: List[str] = Field(default_factory=lambda: ["run"])
    inputs_schema: Dict[str, Any] = Field(default_factory=dict)
    outputs_schema: Dict[str, Any] = Field(default_factory=dict)
    required_algorithms: List[str] = Field(default_factory=list)
    decision_class: str = "advisory"
