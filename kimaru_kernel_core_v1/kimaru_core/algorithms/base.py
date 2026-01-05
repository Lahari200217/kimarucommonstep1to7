from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from kimaru_core.core_context.core_context import CoreContext

class BaseAlgorithm(ABC):
    @abstractmethod
    def describe(self): ...
    @abstractmethod
    def run(self, ctx: 'CoreContext', inputs: Dict[str, Any]) -> Dict[str, Any]: ...
