# Kimaru Kernel Common Core (v1) - Steps 1-5
This repository contains a runnable reference implementation of Kimaru **Kernel Common Core** covering:
- Step 1: repo schema
- Step 2: Agent Fabric OS (registry, security flags, invoker, memory)
- Step 3: Artifacts + Active Pointers + Delta envelopes
- Step 4: Decision Tracker (audit journal) + read models
- Step 5: Governance gateway (intent, ethics/governance policies, approvals)

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .
kimaru-core-demo
```
Then open: http://127.0.0.1:8000/ui

## Notes
- Default persistence uses local SQLite files under `./var/` and artifact blobs under `./var/artifacts/`.
- This is domain-agnostic and does not implement Zone kernels yet.


## Steps 6–7 (Zone contracts + wiring)
This build adds ZoneKernel plug-in contracts, manifest-based zone loading, deterministic boot manager, run coordinator, and precedence resolver.
See `kimaru_core/orchestration/*` and `kimaru_core/runtime/*`.
Example manifest: `examples/kimaru_manifest_example.json`.
