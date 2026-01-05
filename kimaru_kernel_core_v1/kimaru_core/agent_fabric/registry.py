from __future__ import annotations
from typing import Dict, Tuple, Optional, List
from kimaru_core.agent_fabric.descriptor import AgentDescriptor
from kimaru_core.agent_fabric.base_agent import BaseAgent

class AgentFactory:
    def create(self, instance_config: dict, ctx) -> BaseAgent: ...

class AgentRegistry:
    def __init__(self):
        self._factories: Dict[Tuple[str,str], AgentFactory] = {}
        self._descs: Dict[Tuple[str,str], AgentDescriptor] = {}

    def register(self, desc: AgentDescriptor, factory: AgentFactory) -> None:
        key = (desc.agent_type_id, desc.version)
        if key in self._factories:
            raise ValueError(f"Agent already registered: {key}")
        self._factories[key] = factory
        self._descs[key] = desc

    def resolve(self, agent_type_id: str, version: Optional[str] = None) -> tuple[AgentDescriptor, AgentFactory]:
        if version:
            key = (agent_type_id, version)
            if key not in self._factories:
                raise KeyError(f"Agent not found: {key}")
            return self._descs[key], self._factories[key]
        candidates = [k for k in self._factories.keys() if k[0] == agent_type_id]
        if not candidates:
            raise KeyError(f"Agent not found: {agent_type_id}")
        key = sorted(candidates, key=lambda x: x[1])[-1]
        return self._descs[key], self._factories[key]

    def list(self, zone_id: Optional[str] = None) -> List[AgentDescriptor]:
        if not zone_id:
            return list(self._descs.values())
        return [d for d in self._descs.values() if d.zone_id == zone_id]
