# Kernel Common Core Architecture (Steps 1–5)

## Spine
UI (Cockpit) -> Cockpit Gateway -> CoreContext -> (Invokers / Stores / Trackers / Governance)

## Stores
- ArtifactStore (immutable) : filesystem JSON (demo)
- ActivePointerStore (mutable) : SQLite (demo)
- DecisionTracker (audit) : SQLite (demo)
- AgentMemory (KV/log) : SQLite (demo)

## Execution
All agents run via CapabilityInvoker:
PolicyGuard -> Governance pre-check -> agent.run -> artifact/pointer writes -> Governance post-check -> audit events.

## Scripts
Agent scripts are stored as artifacts (kind=agent_script) using KimaruScript DSL v1.
ScriptedAgent executes DSL steps and can:
- run algorithms via AlgorithmRegistry
- store artifacts
- set pointers (governed)
- read/write memory
