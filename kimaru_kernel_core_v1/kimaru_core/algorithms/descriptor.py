from __future__ import annotations
from pydantic import BaseModel
from typing import Any, Dict, Optional

class AlgorithmDescriptor(BaseModel):
    algorithm_id: str
    version: str = "1.0.0"
    inputs_schema: Dict[str, Any] = {}
    outputs_schema: Dict[str, Any] = {}
    determinism_level: str = "deterministic"
    cost_profile: Optional[Dict[str, Any]] = None
