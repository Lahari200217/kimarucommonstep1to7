from __future__ import annotations
from typing import Dict, Tuple, Optional
from kimaru_core.algorithms.descriptor import AlgorithmDescriptor
from kimaru_core.algorithms.base import BaseAlgorithm

class AlgorithmRegistry:
    def __init__(self):
        self._items: Dict[Tuple[str,str], BaseAlgorithm] = {}
        self._desc: Dict[Tuple[str,str], AlgorithmDescriptor] = {}

    def register(self, alg: BaseAlgorithm):
        desc: AlgorithmDescriptor = alg.describe()
        key = (desc.algorithm_id, desc.version)
        if key in self._items:
            raise ValueError(f"Algorithm already registered: {key}")
        self._items[key] = alg
        self._desc[key] = desc

    def resolve(self, algorithm_id: str, version: Optional[str] = None) -> BaseAlgorithm:
        if version:
            key = (algorithm_id, version)
            if key not in self._items:
                raise KeyError(f"Algorithm not found: {key}")
            return self._items[key]
        # pick max version lexicographically (simple for v1)
        candidates = [k for k in self._items.keys() if k[0] == algorithm_id]
        if not candidates:
            raise KeyError(f"Algorithm not found: {algorithm_id}")
        key = sorted(candidates, key=lambda x: x[1])[-1]
        return self._items[key]

    def list(self):
        return list(self._desc.values())
