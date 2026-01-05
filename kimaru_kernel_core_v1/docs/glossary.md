# Kimaru Kernel Common Core Glossary (Steps 1–5)

- **Tenant**: isolated customer/organization boundary.
- **Decision Context**: a stable context for a decision domain within a tenant (e.g., IFIT outbound freight auditing).
- **Session**: a living workspace instance for continuous updates.
- **Epoch**: a versioned checkpoint within a session (monotonic sequence).
- **Run**: a single execution within an epoch (agent execution, simulation, etc.).
- **Artifact**: immutable evidence object (append-only).
- **Active Pointer**: mutable reference to an artifact, used for “latest/approved/active”.
- **Delta**: incremental update artifact that updates a base artifact.
- **Agent**: unit of execution, always invoked via the Agent Fabric.
- **Security Flag**: GREEN (internal), YELLOW (intra), RED (external).
- **Policy Guard**: hard safety/permission gate before execution.
- **Governance Gateway**: ethics + approval enforcement gate.
- **Cockpit Connector**: stable contract for UI to read/control core.
