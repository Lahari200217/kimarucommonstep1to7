"""Manifest API schemas."""

from typing import List, Optional
from pydantic import BaseModel


class ManifestCreateReq(BaseModel):
    """Request to create a new manifest with specified zones."""
    zones: List[str]
    name: Optional[str] = None
    tenant_id: Optional[str] = None


class ManifestCreateResp(BaseModel):
    """Response with created manifest details."""
    manifest_id: str
    location: str
