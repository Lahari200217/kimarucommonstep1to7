from __future__ import annotations
from typing import Dict, Any
from kimaru_core.agent_fabric.base_agent import BaseAgent
from kimaru_core.agent_fabric.descriptor import AgentDescriptor
from kimaru_core.templates.script_dsl.validator import validate_script
from kimaru_core.templates.script_dsl.executor import exec_script
from kimaru_core.artifacts.artifact_ref import ArtifactRef

class ScriptedAgent(BaseAgent):
    def __init__(self, desc: AgentDescriptor, script_ref: ArtifactRef):
        self._desc = desc
        self._script_ref = script_ref

    def describe(self) -> AgentDescriptor:
        return self._desc

    def run(self, ctx, inputs: Dict[str, Any]) -> Dict[str, Any]:
        env = ctx.artifacts.get(self._script_ref)
        script = env.payload
        validate_script(script)
        return exec_script(ctx, self._desc, script, inputs)

class ScriptedAgentFactory:
    def __init__(self, desc: AgentDescriptor, script_ref: ArtifactRef):
        self._desc = desc
        self._script_ref = script_ref

    def create(self, instance_config: dict, ctx) -> BaseAgent:
        # instance_config reserved for future per-instance overrides
        return ScriptedAgent(self._desc, self._script_ref)
