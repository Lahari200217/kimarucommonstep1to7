from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Any, TYPE_CHECKING
from kimaru_core.agent_fabric.descriptor import AgentDescriptor

if TYPE_CHECKING:  # avoid circular imports at runtime
    from kimaru_core.core_context.core_context import CoreContext

class BaseAgent(ABC):
    @abstractmethod
    def describe(self) -> AgentDescriptor: ...
    @abstractmethod
    def run(self, ctx: 'CoreContext', inputs: Dict[str, Any]) -> Dict[str, Any]: ...
