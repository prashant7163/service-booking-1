# Milestone 1 Role and Skill Independence

The application owner approved the following bounded instances for the phase-one plan: `architect-001`, `backend-engineer-001`, `frontend-engineer-001`, `code-reviewer-001`, `build-manager-001`, `quality-engineer-001`, and `independent-auditor-001`. The root `orchestrator-001` is the pre-existing coordinating identity explicitly requested by the owner.

Milestone 1 assignments preserve separation of duties:

- `architect-001` owns architecture and interface decisions only.
- `backend-engineer-001` owns backend and assigned delivery-automation implementation.
- `frontend-engineer-001` owns frontend implementation.
- `code-reviewer-001` independently reviews the exact candidate and does not implement it.
- `build-manager-001` verifies reproducible builds and supply-chain evidence and does not implement the candidate.
- `quality-engineer-001` verifies the supported blast radius independently from implementation.
- `independent-auditor-001` is read-only and reports only to `orchestrator-001`.
- `orchestrator-001` owns coordination, readiness, evidence routing, GitHub reconciliation, and human approval boundaries; it does not substitute for an independent gate role.

The execution safeguards are isolated worktrees, test-driven development, subagent-driven task execution, independent per-task review, and exact-snapshot verification before completion claims.
