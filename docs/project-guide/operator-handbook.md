# Operator handbook

This handbook is the project-local operating guide for the Codex-native Studio workflow.

## First run

1. Run `studioctl doctor` and resolve affected-scope blockers.
2. Run `studioctl status`, open the [discovery guide](discovery.md), and use the [first discovery prompt](first-discovery-prompt.md).
3. Keep the specification in draft until the application owner explicitly approves its exact digest.
4. Use [Codex runtime guidance](runtimes/codex.md) for bounded role activation and handoffs.

## Control commands

`studioctl` exposes status, history, explain, readiness, progress, resume, retry, cancel, checkpoint, projection rebuild, context index rebuild, retention, state/review export, doctor, operator control, capability trust, incident, and conformance commands. Commands that need an initialized run return a structured `not_initialized` result instead of inventing state.

## Approval and recovery

Specification and milestone approval always require a human decision bound to the exact artifact digest. A project-specific skill, expanded agent envelope, or external capability requires its own approval. After interruption, use `studioctl checkpoint`, then `studioctl resume`; only a `safe` marker may continue immediately. `conditional` names the prerequisite, and `invalid` stops.

## Evidence flow

Implementation evidence proceeds through independent Code Review, applicable Build Manager verification, Quality Engineering, Independent Audit to the Orchestrator, and finally user review. A changed executable candidate repeats affected gates. Audit findings never route directly to an implementer.

## Safety

Keep secrets outside repository and Studio state. Pause or stop work with `studioctl control`; controls deny new consequential side effects until exact human clearance. State export is project-relative, redacted, and symlink-safe.

See the [contract guide](contracts.md) for authoritative artifacts.
