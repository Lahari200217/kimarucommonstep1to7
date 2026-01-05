from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List, Tuple

from kimaru_core.artifacts.artifact_ref import ArtifactRef
from kimaru_core.artifacts.active_pointer_store import ActivePointerStore

@dataclass
class PrecedenceResolver:
    """Resolves pointers using a fixed precedence order:

    1) application
    2) custom
    3) zone default
    4) core default
    """

    pointers: ActivePointerStore

    def resolve(self, tenant_id: str, decision_context_id: str, pointer_candidates: List[str]) -> Optional[ArtifactRef]:
        for key in pointer_candidates:
            ref = self.pointers.get_active(tenant_id, decision_context_id, key)
            if ref is not None:
                return ref
        return None

    @staticmethod
    def candidates(core_key: str, *, zone_id: Optional[str]=None, custom_ns: Optional[str]=None, app_ns: Optional[str]=None) -> List[str]:
        # Return candidate keys in precedence order
        keys: List[str] = []
        if app_ns:
            keys.append(f"app/{app_ns}/{core_key}")
        if custom_ns:
            keys.append(f"custom/{custom_ns}/{core_key}")
        if zone_id:
            keys.append(f"zone/{zone_id}/{core_key}")
        keys.append(f"core/{core_key}")
        return keys
