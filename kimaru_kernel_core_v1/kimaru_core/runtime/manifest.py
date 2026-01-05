from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict

class ZoneKernelRef(BaseModel):
    zone_id: str
    package: str
    entrypoint: str  # "module:ClassName" or "module:function"
    version: Optional[str] = None
    enabled: bool = True
    config: Dict[str, str] = Field(default_factory=dict)

class FederationConfig(BaseModel):
    enabled: bool = False
    node_id: Optional[str] = None
    trust_default: Literal["GREEN_INTERNAL","YELLOW_INTRA","RED_EXTERNAL"] = "YELLOW_INTRA"

class KimaruManifest(BaseModel):
    core_version: Optional[str] = None
    zones: List[ZoneKernelRef] = Field(default_factory=list)
    federation: FederationConfig = Field(default_factory=FederationConfig)
