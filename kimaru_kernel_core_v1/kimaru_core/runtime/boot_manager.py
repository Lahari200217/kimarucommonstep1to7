from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from kimaru_core.artifacts.artifact_store import FileSystemArtifactStore
from kimaru_core.artifacts.active_pointer_store import SQLiteActivePointerStore
from kimaru_core.decision_tracker import SQLiteDecisionTracker
from kimaru_core.memory.agent_memory import SQLiteAgentMemory
from kimaru_core.agent_fabric.registry import AgentRegistry
from kimaru_core.algorithms.registry import AlgorithmRegistry
from kimaru_core.agent_fabric.policy_guard import PolicyGuard
from kimaru_core.governance.gateway import GovernanceGateway
from kimaru_core.agent_fabric.observe import ObserveStream

from kimaru_core.runtime.manifest import KimaruManifest
from kimaru_core.orchestration.zone_loader import ZoneKernelLoader
from kimaru_core.orchestration.run_coordinator import RunCoordinator

@dataclass
class BootConfig:
    var_dir: Path
    manifest: Optional[KimaruManifest] = None

@dataclass
class BootManager:
    """Deterministic boot sequence for on-prem Kimaru core runtime.

    This sets up stores/registries and loads enabled ZoneKernels from manifest.
    """

    config: BootConfig

    def boot(self):
        var_dir = self.config.var_dir
        art_dir = var_dir / "artifacts"
        db_dir = var_dir / "db"
        art_dir.mkdir(parents=True, exist_ok=True)
        db_dir.mkdir(parents=True, exist_ok=True)

        artifacts = FileSystemArtifactStore(str(art_dir))
        pointers = SQLiteActivePointerStore(str(db_dir / "pointers.sqlite"))
        tracker = SQLiteDecisionTracker(str(db_dir / "tracker.sqlite"))
        memory = SQLiteAgentMemory(str(db_dir / "memory.sqlite"))

        algorithms = AlgorithmRegistry()
        agents = AgentRegistry()

        policy = PolicyGuard()
        governance = GovernanceGateway()

        observe = ObserveStream()

        zones = {}
        run_coordinator = None
        if self.config.manifest is not None and self.config.manifest.zones:
            loader = ZoneKernelLoader(self.config.manifest)
            zones = loader.bootstrap_all()
            # register zone agents/algorithms
            for z in zones.values():
                z.register(agents, algorithms)
            run_coordinator = RunCoordinator(zones)

        return {
            "artifacts": artifacts,
            "pointers": pointers,
            "tracker": tracker,
            "memory": memory,
            "algorithms": algorithms,
            "agents": agents,
            "policy": policy,
            "governance": governance,
            "observe": observe,
            "zones": zones,
            "run_coordinator": run_coordinator,
        }
