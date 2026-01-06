"""Setup API schemas."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class SetupReq(BaseModel):
    """Request to setup a session with manifest."""
    manifest_location: str
    tenant_id: Optional[str] = None
    session_name: Optional[str] = None


class SetupResp(BaseModel):
    """Response with created session details."""
    session_id: str
    tenant_id: str
    manifest_id: str
    zones_loaded: List[str]
    created_at: str
    state: Dict[str, Any]
