from __future__ import annotations
from typing import Dict

from kimaru_core.orchestration.zone_kernel_interface import ZoneKernel
from kimaru_core.orchestration.zone_models import ZoneRequest, ZoneResult
from kimaru_core.core_context import CoreContext


class Zone1Kernel(ZoneKernel):
    """Minimal example ZoneKernel for demo/discovery tests."""

    def __init__(self, **config: Dict[str, str]):
        self._config = config

    def zone_id(self) -> str:
        return "zone1"

    def kernel_version(self) -> str:
        return self._config.get("version", "0.1.0")

    def register(self, agent_registry, algorithm_registry) -> None:
        return None

    def capability_catalog(self) -> Dict[str, str]:
        return {"noop": "No-op capability for example zone"}

    def execute(self, ctx: CoreContext, request: ZoneRequest) -> ZoneResult:
        return ZoneResult(status="success", explain="Zone1 executed (example)")
