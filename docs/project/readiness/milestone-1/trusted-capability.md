# Milestone 1 Trusted Capabilities

The milestone is limited to capabilities already present locally or explicitly requested by the application owner:

- local Git for source identity and isolated worktrees;
- the configured `studioctl` command for Studio inspection and evidence;
- Java, Node/npm, Docker/Compose, and PostgreSQL-compatible tooling required by the approved stack;
- GitHub CLI/API access solely for the requested milestone/issue synchronization;
- dependency registries required to install the approved locked build dependencies;
- GitHub Actions for pull-request/main validation and non-deploying release artifacts.

No production hosting, cloud database, payment provider, mail provider, registry publication, or deployment capability is approved. Secrets must not be copied into Studio artifacts, logs, issues, test reports, or release manifests. Pull-request validation must use least-privilege permissions and require no publishing credential.
