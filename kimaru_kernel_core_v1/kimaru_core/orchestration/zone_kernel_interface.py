from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict

from kimaru_core.agent_fabric.registry import AgentRegistry
from kimaru_core.algorithms.registry import AlgorithmRegistry
from kimaru_core.core_context import CoreContext

from kimaru_core.orchestration.zone_models import ZoneRequest, ZoneResult

class ZoneKernel(ABC):
    """Abstract plug-in contract for a Kimaru Zone Kernel (zone1..zone5).

    Zone kernels must be independently buildable packages that depend only on kimaru_core.
    Cross-zone logic must be orchestrated through capsule/composite agents using core invoker.
    """

    @abstractmethod
    def zone_id(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def kernel_version(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def register(self, agent_registry: AgentRegistry, algorithm_registry: AlgorithmRegistry) -> None:
        """Register zone agents and algorithms into core registries."""
        raise NotImplementedError

    @abstractmethod
    def capability_catalog(self) -> Dict[str, str]:
        """Expose cockpit-callable operations and descriptions for this zone."""
        raise NotImplementedError

    @abstractmethod
    def execute(self, ctx: CoreContext, request: ZoneRequest) -> ZoneResult:
        """Execute a zone run. Must use core invoker for any agent execution."""
        raise NotImplementedError
