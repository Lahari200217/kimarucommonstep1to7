from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional, Literal
from kimaru_core.utils.time import utc_now_iso

class TrackEvent(BaseModel):
    event_id: str
    created_at: str = Field(default_factory=utc_now_iso)
    tenant_id: str
    decision_context_id: str
    session_id: str
    epoch_id: str
    run_id: str
    zone_id: str

    actor_type: Literal["human","agent","system"] = "system"
    actor_id: str = "system"
    actor_display_name: Optional[str] = None

    event_type: str
    severity: Literal["INFO","WARN","ERROR","CRITICAL"] = "INFO"
    message: str = ""
    refs: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
