# Milestone-one foundation contract

Contract ID: `contract-m1-foundation`. Contract version: `1.0.0`. Architecture decision: `architecture-decision-m1-foundation-001`. Author: `architect-001`. Milestone: `milestone-foundation-delivery`. Date: 2026-09-10.

Status: architecture and interface alignment artifact for Orchestrator readiness assembly. This document supplies the contract-snapshot content and architecture decision; it is not the schema-validated Studio `ContractSnapshot`, a ready outcome, implementation authorization, or independent approval. No application, configuration, workflow, or migration is implemented here.

## Authority and exact inputs

The approved specification is `docs/discovery/project-specification.json`, approval `apr-service-booking-1-spec-001`, canonical approved digest `637f0e2082e73bd106a246d7bf47034943b41724db78fb828ccd028aa638e202`. The approved plan is `docs/project/planning/phase-one-milestone-plan.json`, approval `apr-service-booking-1-plan-001`, approved subject digest `7f601a82fae72d191db3344eaef7f5727b399e89b293cc903cb810dd2671fce0`. These canonical subject digests are distinct from file-byte hashes.

| Inspected input | SHA-256 of file bytes |
| --- | --- |
| `docs/discovery/project-specification.json` | `49464b8bc24216de31a1d3ea2c6251051f5311d306aa5eba5e30f4dce7006356` |
| `docs/project/planning/phase-one-milestone-plan.json` | `5516c48eb7557727f2de2c20915391e77e508df970a241e96be8efa6cc1bb79c` |
| `docs/superpowers/plans/2026-09-10-service-booking-phase-one.md` | `3fbb9d1c07510f2ff3bb7f95da9e1bd4cb0ef18cf8474fde3ca73abf49977dd0` |
| `docs/project/planning/phase-one-plan-approval.json` | `fbaca65a0090f68b3a93461528c66ce4e09c225b5a0a86438fb9c569ffc701c4` |

`AGENTS.md`, `.codex/agents/architect.toml`, `studio.yaml`, and `shared/contracts/contract-snapshot.schema.json` govern this output. The initial `studioctl status` invocation failed because the command was absent from PATH. The Orchestrator supplied `/Users/pacific/Playground/AIDevStudio/.venv/bin/studioctl`; that command succeeded and reported `phase: new`. At final verification, `git rev-parse HEAD` returns governance baseline `ea752c521becff2c3b3926f66beea0480e471bbd`; the earlier unborn-repository condition is resolved. This document is a readiness addition built on that baseline; its incorporated version is identified by its containing Git commit and byte hash. The Orchestrator reports that the installed Studio command is a scaffold hard-coding `phase: new`, with lifecycle commands returning `not_initialized`; formal lifecycle readiness remains blocked on a supported control-plane path.

## Architecture decision and module boundary

Use the approved monorepo and modular Spring application. The backend is the sole owner of authorization and durable business state. The frontend renders server results and consumes HTTP DTOs; it has no database connection and receives no persistence entities. One PostgreSQL database holds application and JDBC-session data. Simulated email, payment, and notification ports remain backend interfaces in later milestones.

```text
backend/                         Java 21 / Spring Boot 4.1.1; ch.servicebooking
  src/main/java/ch/servicebooking/{config,health}/
  src/main/resources/db/migration/
frontend/                        React 19.3 / TypeScript / Vite 8; Node 22 build
  src/{app,api}/
e2e/                             browser infrastructure; full journeys in M4
docs/api/openapi.yaml             source HTTP contract
docs/architecture/               decisions and versioned contract snapshots
scripts/ci/                      shared local/runner entry points
scripts/release/                 archives, OCI assembly, reproducibility
.github/workflows/               PR/main checks and non-deploying artifacts
docs/project/progress/           authoritative progress and remote mappings
compose.yaml                     local database/application wiring
Makefile                         stable developer/CI commands
```

The browser uses one origin. During local development, Vite proxies `/api` to the backend; the built frontend's serving container routes `/api` to the backend. The proxy preserves `/api/v1` without stripping or duplicating it. Example: browser `GET http://localhost:5173/api/v1/health` forwards to `http://localhost:8080/api/v1/health`. Browser code never embeds the internal Compose hostname or an external API origin. A static asset request such as `/assets/app.js` remains with the frontend server. Example Compose service names for this contract are `db`, `backend`, and `frontend`; backend HTTP port is `8080`, PostgreSQL port is `5432`, and the frontend serving container listens on `8080` internally.

Java 21, Spring Boot 4.1.1, React 19.3, Vite 8, and Node 22 are approved version constraints, not a claim that the full dependency graph has already resolved. Freeze the verified package selections `react@19.3.0`, `vite@8.0.0`, `typescript@5.9.3`, `vitest@4.0.18`, and `openapi-typescript@7.10.1`. Public registry metadata was read on 2026-09-10: [React](https://registry.npmjs.org/react/19.3.0), [Vite](https://registry.npmjs.org/vite/8.0.0), [TypeScript](https://registry.npmjs.org/typescript/5.9.3), [Vitest](https://registry.npmjs.org/vitest/4.0.18), [OpenAPI TypeScript](https://registry.npmjs.org/openapi-typescript/7.10.1). Vite's engine requires Node `^20.19.0 || >=22.12.0`; within the approved Node 22 family this contract therefore requires Node 22.12.0 or later 22.x. The generator requires TypeScript 5.x, satisfied by the selected TypeScript pin. Metadata availability does not prove a successful install/build.

Maven Wrapper, explicit dependency/plugin versions, an npm lockfile and `npm ci` make the installed inputs reviewable. Backend and frontend containers use pinned base-image digests and fixed target architecture for comparable outputs. Exact Node/npm/JDK builds, React DOM/types, Testing Library, jsdom, Playwright, wrapper/plugin versions, and compatible base-image selection remain Build Manager verification conditions; do not silently substitute another approved runtime family. PostgreSQL exact major/patch and image digest are a coordinated implementation input, identical for Compose and Testcontainers (G3). This records unevidenced pins honestly instead of claiming fabricated registry resolution.

## Versioned HTTP and generated-client interface

Interface `if-m1-http`: producer `task-m1-backend-foundation`, consumers `task-m1-frontend-foundation` and `task-m1-delivery-automation`, contract owner `task-m1-architecture`.

`docs/api/openapi.yaml` is the authoritative HTTP shape. Use OpenAPI 3.1.0 for the initial document and stable operation ID `getHealth`. Contract-first edits precede producer/consumer changes. Java DTOs implement the schema; JPA entities are never the public schema. Generate TypeScript schema/operation types with locked `openapi-typescript@7.10.1` in the direction `OpenAPI -> frontend/src/api/generated/schema.ts`; frontend owns the command and output, architecture owns the input. Keep credentials, CSRF, problem-response handling and the small fetch transport authored in `frontend/src/api/client.ts`. Do not hand-edit generated output. `npm run generate:api` runs `openapi-typescript ../docs/api/openapi.yaml -o src/api/generated/schema.ts`. `npm run check:api` generates into a temporary file, byte-compares it with the committed output, and exits nonzero on drift; it must detect a missing/untracked generated file as well as stale content. Consumers import generated `HealthResponse` schema types; a duplicated handwritten schema is not the completed M1 contract.

```http
GET /api/v1/health HTTP/1.1
Accept: application/json

HTTP/1.1 200 OK
Content-Type: application/json

{"status":"UP"}
```

The sole M1 application route is public and returns exactly this minimal status data. It discloses no environment, dependency versions, database identifiers, credentials, or stack traces. Successful application startup includes Flyway validation/application against PostgreSQL. `UP` means the application endpoint is responding; it is not a continuous database-readiness assertion. The integration test separately queries PostgreSQL and verifies the migration history, so HTTP health alone cannot satisfy the database smoke criterion.

Use the existing planned `api.get<T>(path: string): Promise<T>` contract with a path relative to `/api/v1`. Example: `api.get<HealthResponse>('/health')` fetches `/api/v1/health` using `credentials: 'include'`. Reject absolute URLs and paths already prefixed with `/api/v1`; this avoids an accidental credential-bearing call outside the application. A non-2xx response rejects, a malformed successful JSON response is a contract failure, and the shell renders localized unavailable/error state without displaying raw diagnostics.

Interface `if-m1-errors`: backend produces `application/problem+json` using the approved RFC 9457 direction; frontend consumes status plus stable `code`. Define `type`, `title`, `status`, `detail`, `instance`, and extension `code`; these are the required baseline fields. `instance` is the request path without query parameters. `detail` is safe generic text, not exception content. The frontend localizes by `code`, with a generic fallback for unknown codes. A network/non-JSON failure is a transport error and must not be cast to a valid problem document.

```http
HTTP/1.1 403 Forbidden
Content-Type: application/problem+json

{"type":"urn:servicebooking:problem:forbidden","title":"Forbidden","status":403,"detail":"This action is not permitted.","instance":"/api/v1/provider/shop","code":"FORBIDDEN"}
```

The example provider route illustrates the later security boundary and does not add it to M1. Reserve `VALIDATION_ERROR`/400, `UNAUTHENTICATED`/401, `FORBIDDEN`/403, `NOT_FOUND`/404, `CONFLICT`/409, and `INTERNAL_ERROR`/500. Security-filter errors use the same JSON envelope and do not redirect the SPA to HTML login. Unknown API paths do not fall through to the SPA index page. Additive optional fields may remain in v1; removed/renamed fields, changed semantics, or new required request fields require an explicitly reviewed contract change before consumers integrate.

## Database, migration, and clock interface

Interface `if-m1-persistence`: backend foundation owns Flyway and connection consumption; delivery automation consumes the same database settings through local/CI orchestration. Only the backend accesses PostgreSQL. The frontend has no `SPRING_DATASOURCE_*` or database secret inputs.

```text
SPRING_DATASOURCE_URL=jdbc:postgresql://db:5432/service_booking
SPRING_DATASOURCE_USERNAME=<runtime-injected application identity>
SPRING_DATASOURCE_PASSWORD=<runtime-injected secret>
```

Angle-bracket values above denote injection points and are not credentials. Local/CI instances use synthetic data and ephemeral secrets. Real hosted application data, including backups, requires Switzerland; no hosting or rollout is introduced in M1. Avoid database-volume contents in CI uploads and never publish populated database images.

`backend/src/main/resources/db/migration/V1__foundation.sql` is the sole M1 schema migration. Flyway owns schema evolution and migration history; JPA validates mappings and never creates/updates schema. Disable competing Spring SQL/session auto-initializers. Any JDBC session tables needed in M1 are created by V1. V2 owns identity/catalog later, V3 commerce, and V4 fulfillment; already-applied migration contents are immutable. Coordinating new version numbers belongs to the backend owner through the Orchestrator, not concurrent ad hoc SQL writers. The fresh-database test and repeat startup verify migrations do not duplicate initialization.

Inject `java.time.Clock` from `ClockConfig` with UTC default, rather than scattering system-clock calls. Example test seam: `Clock.fixed(Instant.parse("2026-09-10T12:00:00Z"), ZoneOffset.UTC)`. Persist future business instants as UTC instants/`timestamptz`; later UI input converts `Europe/Zurich` to an instant. Future monetary DTOs use decimal strings and `currency: 'CHF'`, for example `{"unitPrice":"45.00","currency":"CHF"}`; durable arithmetic uses decimal types, never browser-authoritative floating-point totals. Those domain fields are reserved for later contracts and are not V1 tables.

## Authentication and role trust boundary

Interface `if-m1-session`: M1 establishes Spring Security defaults and a compatible same-origin transport; M2 adds actual registration, verification, sign-in and session operations. Allow the public health route explicitly and deny protected requests server-side. Do not provide default in-memory demo credentials, wildcard credentialed CORS, or a blanket permit-all rule for future API routes.

The planned mechanism is JDBC-backed opaque cookie sessions. The session identifier cookie is `SESSION`, `HttpOnly`, `SameSite=Lax`, path `/`, with `Secure` required for HTTPS and any hosted configuration. Only a clearly local HTTP profile may disable `Secure`. Do not put session credentials in localStorage or DTOs. Spring Security CSRF protection remains enabled for unsafe cookie-authenticated methods; M2 will freeze the CSRF bootstrap endpoint/cookie details before auth implementation. Reserve the conventional `X-XSRF-TOKEN` request header and `XSRF-TOKEN` readable CSRF cookie, which is distinct from the HttpOnly session credential. Sign-in rotates the session identifier; sign-out invalidates it when M2 implements those operations.

```http
POST /api/v1/provider/shop HTTP/1.1
Cookie: SESSION=<opaque session>; XSRF-TOKEN=<csrf token>
X-XSRF-TOKEN: <same csrf token>
Content-Type: application/json
```

This is an interface example, not a runnable request or an M1 endpoint. Missing/invalid CSRF proof rejects unsafe operations. Role values are `CUSTOMER`, `PROVIDER`, `ADMIN`; roles come from the authenticated server principal and never from a trusted request body. A customer/provider account cannot have both personas. Ownership is checked in backend services/queries even after role checks. Example later behavior: customer A requesting customer B's cart is denied; a provider cannot publish until verified; a suspended provider cannot sign in. Customer verification gates reservations. Passwords use BCrypt in M2; simulated delivery ports must not place usable verification/reset tokens, session IDs or redemption codes in logs or public responses. No administrator self-registration route is inferred.

## CI, release, and tracking interfaces

Interface `if-m1-ci`: the delivery package owns stable root commands. `make test` runs backend PostgreSQL integration tests plus frontend checks/tests/build; `make e2e` exercises the built frontend against the backend/PostgreSQL through the browser seam; `make artifacts` assembles archives and runnable OCI archives for the exact validated revision. Each required command exits nonzero on failure. Freeze backend local/CI command `./mvnw -B verify`, with Maven Surefire for unit tests and Maven Failsafe bound to integration-test/verify for `**/*IT.java`. The approved `HealthControllerIT` must appear in `backend/target/failsafe-reports/`; default test-discovery assumptions cannot substitute for that report. This corrects the plan's illustrative `test` command so integration-test failure actually blocks validation. Frontend commands are `npm ci`, `npm run check:api`, `npm run typecheck`, `npm test -- --run`, and `npm run build`; browser installation/runner commands are `npm ci` and `npx --no-install playwright test` from `e2e/`, with browser binaries installed at the locked Playwright version by the CI setup step.

PR and main workflows run the same scoped baseline. A backend or browser failure blocks the release path. M1 browser coverage is shell/health at 390px and 1280px; full product journeys remain M4. Delivery owns the minimal browser harness under the resolved G2 allocation. Freeze checks for a successful same-origin API health request, localized shell status, English/German language toggle, keyboard-operable language control with an accessible name, visible focus, and no horizontal page overflow at both widths. Frontend owns minimal `src/i18n/{index.ts,en.ts,de.ts}` bootstrap in M1; the M2 task extends these files. Include frontend failure-state fixture coverage so unavailable API status remains understandable. Test reports identify source commit, run ID, commands, test counts/results, and redacted diagnostics. Example evidence reference: `{ "sourceRevision": "<40-hex commit>", "validationRunId": "<run id>", "report": "backend/target/failsafe-reports/TEST-ch.servicebooking.health.HealthControllerIT.xml" }`. This example has metavariables and is not asserted evidence.

Interface `if-m1-release`: release workflows consume successful exact-revision main-run outputs, not arbitrary files from another branch or run. `workflow_dispatch` is an entry point, never a validation bypass. `workflow_call` inherits the caller's exact source identity and success gates. Downloaded artifact identities/checksums must be verified. Use commit-addressed versions and record the requested platform, locked-input hashes and successful run link in `dist/manifest.json`. The approved minimum keys are retained; the spec-required provenance fields extend them:

```json
{
  "sourceRevision": "<40-hex validated main commit>",
  "backendSha256": "<64-hex backend archive checksum>",
  "frontendSha256": "<64-hex frontend archive checksum>",
  "backendImageDigest": "sha256:<64-hex OCI manifest digest>",
  "frontendImageDigest": "sha256:<64-hex OCI manifest digest>",
  "validationRun": {"id": "<successful run id>", "url": "<successful run URL>"},
  "toolchains": {"java": "<exact Java 21 build>", "node": "<exact Node 22 patch>", "maven": "<wrapper version>"},
  "lockedInputs": {"backendPomSha256": "<64-hex>", "frontendLockSha256": "<64-hex>", "baseImageDigests": ["sha256:<64-hex>"]},
  "platform": "linux/amd64",
  "evidence": ["<backend report>", "<frontend report>", "<browser report>"]
}
```

These examples define value kinds; actual artifacts must contain validated real values, never metavariables. `backendSha256`/`frontendSha256` name the downloadable archive bytes, and OCI image digests name OCI manifests, not tar-file checksums. Normalize archive ordering, ownership, timestamps and compression inputs. Use a source-derived epoch and exclude run-varying provenance from reproducible payloads. The reproducibility command rebuilds locked inputs twice and compares application payload checksums; it separately records container digests and any intentionally varying provenance. Artifact names and their checksum mapping are frozen by delivery automation in the manifest/assembler together, before integration. Build/archive generation has no registry push, GitHub Release publication, rollout or environment deployment authority.

Interface `if-m1-tracking`: `docs/project/progress/github-sync.yaml` defines `local_id`, `github_url`, `milestone`, `status`, `last_synced_at`. Example unsynchronized local row:

```yaml
local_id: task-m1-backend-foundation
github_url: null
milestone: milestone-foundation-delivery
status: ready
last_synced_at: null
```

`ready` here illustrates a local status value, not this task's current Studio state. Populate URL and UTC synchronization timestamp only after successful authorized reconciliation. Remote edits/closures cannot change local approval. A failed sync preserves the row and a redacted actionable retry marker, for example `{ "local_id": "task-m1-backend-foundation", "operation": "update-counterpart", "reason": "remote unavailable", "retry_from": "local authoritative record" }`. Synchronization checkpoints remain approved registration, work start, block/resume, verification handoff, and recorded human milestone decision. The Orchestrator owns external coordination and lifecycle evidence; this Architect assignment performs neither.

## Integration seams and threat controls

| Interface | Required M1 evidence | Owner |
| --- | --- | --- |
| `if-m1-http`, `if-m1-errors` | Contract lint, backend health JSON/content type, denied/error JSON, frontend success/error fixtures matching schema | Architecture contract; backend and frontend implementation |
| `if-m1-persistence` | Testcontainers real PostgreSQL, V1 migration history, explicit database query, repeat initialization; no H2 substitute | Backend foundation |
| `if-m1-session` | Public health works anonymously; protected request fails; unsafe request lacks CSRF and fails; no public diagnostic/secret fields | Backend foundation |
| `if-m1-ci` | `*IT` appears in report, component tests/build, shell browser smoke at both widths, deliberately failed backend/browser check prevents release | Delivery automation with backend/frontend outputs |
| `if-m1-release` | Wrong-revision/unvalidated run rejected; exact-revision archives and OCI images; two-build payload comparison | Delivery automation; independently verified by Build Manager |
| `if-m1-tracking` | Mapping identity preserved through simulated synchronization failure; no remote approval inference | Delivery automation; Orchestrator coordinates remote work |

M1 extends the approved embedded threat model for the newly affected foundation boundaries:

| Control ID / boundary | Abuse and asset | Required control and evidence | Residual/deferred scope |
| --- | --- | --- | --- |
| `ctrl-m1-browser-api` | Forged cookie-authenticated requests; session theft; cross-role access | Same-origin transport, cookie attributes, CSRF enforcement, explicit public allowlist; negative backend tests and safe frontend errors | M2 owns authentication and principal lifecycle; M1 is not a complete authentication system |
| `ctrl-m1-db` | Public database/credentials; destructive implicit schema updates | Backend-only database connectivity, injected secrets, Flyway-only migrations, real PostgreSQL tests; synthetic fixtures | Swiss production topology/backups/retention require later review |
| `ctrl-m1-redaction` | Tokens/PII escape through HTTP errors, logs, artifacts or GitHub | Generic problem details, no diagnostic public health, exclude environment dumps/database volumes, redact fixtures/reports before persistence/export | No production security certification |
| `ctrl-m1-pr-runner` | Untrusted PR extracts publishing credentials or contaminates trusted release | Read-only default workflow permissions, no publishing secrets in PR jobs, pinned actions/tools, no privileged execution of PR code, release input verification | External capability trust is an Orchestrator readiness responsibility |
| `ctrl-m1-release` | Failed or substituted revision masquerades as release | Main/exact-SHA/success identity check, checksum verification, immutable artifact identity, negative gating and reproducibility evidence | Registry and deployment destination remain unapproved |
| `ctrl-m1-local-authority` | Remote status masquerades as approval or outage loses progress | Stable mapping IDs, local authority, durable retry marker, explicit exact-digest human decision | Remote availability can lag |

Future code guessing, overselling, duplicate checkout, persistent cart hoarding, and administrator misuse remain governed by the approved threat model and M2–M4 contracts. M1 does not add automatic cart expiry, booking-level attempt blocks, new administrator actions, or real external delivery.

## Exact work-package assignments and dependencies

Use the approved task IDs as work-package IDs; do not invent a second identity mapping. Architecture is sequence 1; backend/frontend are sequence 2 and may run concurrently; delivery is sequence 3 after both. Worktree allocation must happen through the Orchestrator after readiness. These are the approved workspace locators, not existing worktree claims.

| Work package | Owner | Dependencies | Workspace |
| --- | --- | --- | --- |
| `task-m1-architecture` | `architect-001` | none | `worktrees/m1-architecture` |
| `task-m1-backend-foundation` | `backend-engineer-001` | `task-m1-architecture` | `worktrees/m1-backend` |
| `task-m1-frontend-foundation` | `frontend-engineer-001` | `task-m1-architecture` | `worktrees/m1-frontend` |
| `task-m1-delivery-automation` | `backend-engineer-001` | `task-m1-backend-foundation`, `task-m1-frontend-foundation` | `worktrees/m1-delivery` |

Planned owned files and narrowly resolved child locators:

1. `task-m1-architecture`: `docs/architecture/adr-001-monorepo-runtime.md`, `docs/architecture/contracts/m1-foundation.yaml`, `docs/api/openapi.yaml`, initial `docs/project/progress/github-sync.yaml`. The current readiness-only dispatch owns just `docs/architecture/milestone-1-foundation-contract.md`; the other documents are planned outputs, not written here. Integration references: this contract, OpenAPI, foundation YAML, initial tracking schema.
2. `task-m1-backend-foundation`: `backend/pom.xml`, `backend/.mvn/wrapper/maven-wrapper.properties`, `backend/mvnw`, `backend/src/main/java/ch/servicebooking/ServiceBookingApplication.java`, `backend/src/main/java/ch/servicebooking/config/{ClockConfig,SecurityConfig}.java`, `backend/src/main/java/ch/servicebooking/health/HealthController.java`, `backend/src/main/resources/{application.yml,application-test.yml}`, `backend/src/main/resources/db/migration/V1__foundation.sql`, `backend/src/test/java/ch/servicebooking/health/HealthControllerIT.java`. The Orchestrator's readiness clarification adds `backend/Dockerfile` and initial `compose.yaml` database wiring to this owner's foundation package. Integration references: OpenAPI health/errors, runtime/database/clock contract, backend report and runnable container.
3. `task-m1-frontend-foundation`: `frontend/{package.json,package-lock.json,tsconfig.json,vite.config.ts,index.html}`, `frontend/src/{main.tsx,app/App.tsx,app/router.tsx,api/client.ts,styles.css}`, `frontend/src/app/App.test.tsx`. Child locators within `frontend/` include `frontend/Dockerfile`, `frontend/nginx.conf` for static serving and the same-origin proxy, `frontend/src/api/generated/schema.ts`, generator/stale-check scripts under `frontend/scripts/`, and `frontend/src/i18n/{index.ts,en.ts,de.ts}` for the M1 language bootstrap. Integration references: OpenAPI, relative-path typed client, built assets/container, component reports.
4. `task-m1-delivery-automation`: `compose.yaml` (integration after backend handoff), `Makefile`, `.tool-versions`, `scripts/ci/{backend.sh,frontend.sh,e2e.sh,all.sh,workflow-contract.sh}`, `scripts/release/{build-artifacts.sh,verify-reproducibility.sh}`, `.github/workflows/{ci.yml,release-artifacts.yml}`, `.github/{ISSUE_TEMPLATE/work-item.yml,PULL_REQUEST_TEMPLATE.md}`, `docs/project/progress/PROGRESS.md`. Tracking row updates in `docs/project/progress/github-sync.yaml` follow architecture handoff, so ownership is sequential. Delivery consumes backend/frontend Dockerfiles without concurrently editing their package-owned files. Integration references: shell browser seam, reports, manifest, payload checksums/OCI digests, tracker mappings. Resolved browser child locators are `e2e/{package.json,package-lock.json,playwright.config.ts}` and `e2e/tests/foundation.spec.ts`; M4 extends this harness with its separately approved journeys and fixtures.

The explicit Compose ownership sequence is the Orchestrator's 2026-09-10 readiness clarification: backend creates database wiring; delivery owns final application/root assembly only after backend/frontend complete. No parallel writer may modify `compose.yaml`. Any change to a completed producer-owned container or source package is returned to that owner through the Orchestrator.

## Load-bearing gaps and safe resume

G1 — Formal state/snapshot: successful `studioctl status` reports `new`; the Orchestrator's source inspection identifies an uninitialized scaffold without a supported lifecycle transition. The baseline commit now exists at `ea752c521becff2c3b3926f66beea0480e471bbd`, resolving the earlier missing-HEAD problem. The Orchestrator must reconcile approved artifacts through a supported control-plane path, include readiness additions in an exact snapshot, and assemble/validate the real readiness and `ContractSnapshot` records. This Markdown cannot claim a ready outcome. Use `studioctl explain` before any transition. No transition is attempted in this assignment.

G2 — Resolved browser ownership: the Orchestrator assigns minimal M1 shell/health Playwright infrastructure to the existing delivery package, with explicit child locators above. Full catalog/commerce/fulfillment/admin journeys remain M4. A green no-op browser job does not meet the contract.

G3 — Locked runtime inputs: five frontend package selections have verified registry metadata and are frozen above, including generator version. PostgreSQL exact version/digest, JDK/Node/npm builds, remaining frontend/test packages, wrapper/plugins, action pins, and base-image digests have not been resolved or tested in this planning-only task. The Orchestrator/Build Manager must record concrete compatible inputs and successful locked dependency resolution as a readiness/build condition; backend and Compose/Testcontainers must agree. Approved Java/Spring/React/Vite/Node constraints may not be silently changed if resolution fails.

G4 — Container child-locator clarification is resolved by the Orchestrator dispatch message and recorded above; formal readiness assignments must carry it forward. Serving configuration belongs to frontend, database-first Compose to backend, and final root/release assembly to delivery.

Safe-resume marker: `architect-001` has completed the bounded contract draft and returns it to the Orchestrator for readiness assembly. Resume by verifying the four input hashes, baseline commit and this file's recorded handoff hash, resolving G1/G3 and carrying the G2/G4 allocations into the formal work-package record. Do not treat this draft or elapsed time as human approval. Only the Orchestrator may assign follow-up work; independently reviewed implementation remains a later gate.

Evidence commands executed during this assignment: `/Users/pacific/Playground/AIDevStudio/.venv/bin/studioctl status`; `git rev-parse HEAD` (final result is the baseline commit above); `git status --short`; `shasum -a 256` on the four inputs listed above; `jq` inspection of milestone IDs, task owners/dependencies, approval and specification boundaries; read-only `curl` of the five linked registry endpoints (successful after sandbox DNS prevented the initial network read). No build/test success is claimed because no executable implementation was part of this task. At handoff, run `git diff --check --no-index /dev/null docs/architecture/milestone-1-foundation-contract.md` and `shasum -a 256 docs/architecture/milestone-1-foundation-contract.md` for this exact document.
