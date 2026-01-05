from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from kimaru_core.identity.models import TenantRef, DecisionContextRef, SessionContext, EpochContext, RunContext, ActorRef, TraceContext, FederationContext
from kimaru_core.artifacts.artifact_store import ArtifactStore
from kimaru_core.artifacts.active_pointer_store import ActivePointerStore
from kimaru_core.decision_tracker.tracker import DecisionTracker
from kimaru_core.agent_fabric.registry import AgentRegistry
from kimaru_core.agent_fabric.policy_guard import PolicyGuard
from kimaru_core.governance.gateway import GovernanceGateway
from kimaru_core.agent_fabric.observe import ObserveStream
from kimaru_core.memory.agent_memory import AgentMemory
from kimaru_core.algorithms.registry import AlgorithmRegistry

@dataclass
class CoreContext:
    tenant: TenantRef
    decision_context: DecisionContextRef
    session: SessionContext
    epoch: EpochContext
    run: RunContext
    actor: ActorRef
    trace: TraceContext
    federation: FederationContext

    artifacts: ArtifactStore
    pointers: ActivePointerStore
    tracker: DecisionTracker
    agents: AgentRegistry
    algorithms: AlgorithmRegistry
    policy: PolicyGuard
    governance: GovernanceGateway
    observe: ObserveStream
    memory: AgentMemory

    allow_external: bool = False
    debug: bool = False
