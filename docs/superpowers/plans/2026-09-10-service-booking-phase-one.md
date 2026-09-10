# Service Booking Marketplace Phase One Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver the approved basic Switzerland-focused service-booking marketplace, its automated verification, synchronized GitHub tracking, and reproducible non-deploying release artifacts.

**Architecture:** Use a monorepo with a Java 21 / Spring Boot 4.1.1 REST API, PostgreSQL, Flyway migrations, and a React 19.3 TypeScript SPA built with Vite 8. The API owns authorization, inventory, price snapshots, checkout, redemption, expiry, and administration; the SPA consumes versioned `/api/v1` contracts. Docker Compose supplies local PostgreSQL, while GitHub Actions reproduces backend, frontend, Playwright, and release-artifact checks.

**Tech Stack:** Java 21, Spring Boot 4.1.1, Maven Wrapper, PostgreSQL, Flyway, Spring Security/Session/JPA, Testcontainers, React 19.3, TypeScript, Vite 8, Vitest, Testing Library, Playwright, Docker Compose, GitHub Actions.

**Spec:** `docs/discovery/project-specification.json` approved as `apr-service-booking-1-spec-001`, canonical digest `637f0e2082e73bd106a246d7bf47034943b41724db78fb828ccd028aa638e202`.

## Global Constraints

- Local Studio artifacts remain authoritative; GitHub milestones/issues are synchronized counterparts and never confer approval.
- All hosted application data must remain in Switzerland; local and CI tests use synthetic data.
- Customer and provider accounts are separate. Customer-provider messaging, refunds, self-service deletion, cancellation, rescheduling, staff, and automatic cart expiry are absent.
- All customer/provider workflows must work at mobile and desktop widths and support English/German UI copy.
- Use CHF tax-inclusive prices with two decimals; one current unit price applies to every slot of an offering.
- Inventory updates, selected checkout, and payment outcomes must be transactional, idempotent, and nonnegative.
- Every executable milestone follows test-first implementation, independent Code Review, Build verification, Quality Engineering, Independent Audit, then user review.
- Exact dependency versions are committed in Maven and npm lock files; CI uses Java 21 and Node 22.

## Repository map

```text
backend/                         Spring Boot API and backend tests
frontend/                        React SPA and unit/component tests
e2e/                             Playwright configuration, fixtures, and journeys
.github/workflows/               pull-request/main CI and release-artifact workflow
scripts/ci/                      local equivalents of CI jobs
scripts/release/                 normalized artifact and manifest creation
docs/api/openapi.yaml            versioned REST contract
docs/architecture/               ADRs and milestone contract snapshots
docs/project/progress/           authoritative local progress and GitHub mapping
compose.yaml                     local PostgreSQL and application composition
Makefile                         stable build, test, and run entry points
```

---

## Milestone 1 — Foundation and delivery automation

### Task 1: Freeze foundation contracts

**Files:**
- Create: `docs/architecture/adr-001-monorepo-runtime.md`
- Create: `docs/architecture/contracts/m1-foundation.yaml`
- Create: `docs/api/openapi.yaml`
- Create: `docs/project/progress/github-sync.yaml`

**Interfaces:**
- Produces: `/api/v1/health`; Java package root `ch.servicebooking`; frontend API base `/api/v1`; tracker fields `local_id`, `github_url`, `milestone`, `status`, `last_synced_at`.

- [ ] **Step 1: Write contract checks** in `docs/architecture/contracts/m1-foundation.yaml` for Java 21, Node 22, PostgreSQL, same-origin cookie sessions, CI commands, artifact manifests, and redaction.
- [ ] **Step 2: Validate the checks fail** because the referenced files do not exist: `test -f backend/pom.xml && test -f frontend/package.json && test -f compose.yaml`; expected exit code `1`.
- [ ] **Step 3: Write the ADR and OpenAPI health contract** with this response shape:

```yaml
/api/v1/health:
  get:
    responses:
      '200':
        content:
          application/json:
            schema:
              type: object
              required: [status]
              properties:
                status: { type: string, enum: [UP] }
```

- [ ] **Step 4: Validate YAML and references:** `ruby -e 'require "yaml"; ARGV.each { |f| YAML.load_file(f) }' docs/architecture/contracts/m1-foundation.yaml docs/api/openapi.yaml docs/project/progress/github-sync.yaml`; expected pass.
- [ ] **Step 5: Commit:** `git add docs/architecture docs/api docs/project/progress/github-sync.yaml && git commit -m "docs: freeze foundation contracts"`.

### Task 2: Build the backend foundation

**Files:**
- Create: `backend/pom.xml`, `backend/.mvn/wrapper/maven-wrapper.properties`, `backend/mvnw`
- Create: `backend/src/main/java/ch/servicebooking/ServiceBookingApplication.java`
- Create: `backend/src/main/java/ch/servicebooking/config/{ClockConfig,SecurityConfig}.java`
- Create: `backend/src/main/java/ch/servicebooking/health/HealthController.java`
- Create: `backend/src/main/resources/{application.yml,application-test.yml}`
- Create: `backend/src/main/resources/db/migration/V1__foundation.sql`
- Test: `backend/src/test/java/ch/servicebooking/health/HealthControllerIT.java`

**Interfaces:**
- Produces: `GET /api/v1/health -> HealthResponse(String status)`; PostgreSQL connection from `SPRING_DATASOURCE_*`; UTC persistence clock.

- [ ] **Step 1: Write `HealthControllerIT`** using `@SpringBootTest`, Testcontainers PostgreSQL, and `MockMvc` to expect `{"status":"UP"}`.
- [ ] **Step 2: Run:** `cd backend && ./mvnw -q -Dtest=HealthControllerIT test`; expected failure because the application and endpoint are absent.
- [ ] **Step 3: Implement the minimal application and endpoint:**

```java
public record HealthResponse(String status) {}

@RestController
@RequestMapping("/api/v1/health")
final class HealthController {
  @GetMapping HealthResponse health() { return new HealthResponse("UP"); }
}
```

- [ ] **Step 4: Run:** `cd backend && ./mvnw -q test`; expected pass with Flyway applied to Testcontainers PostgreSQL.
- [ ] **Step 5: Commit:** `git add backend && git commit -m "feat: establish backend foundation"`.

### Task 3: Build the frontend foundation

**Files:**
- Create: `frontend/{package.json,package-lock.json,tsconfig.json,vite.config.ts,index.html}`
- Create: `frontend/src/{main.tsx,app/App.tsx,app/router.tsx,api/client.ts,styles.css}`
- Test: `frontend/src/app/App.test.tsx`

**Interfaces:**
- Consumes: `GET /api/v1/health`.
- Produces: `api.get<T>(path: string): Promise<T>` and responsive application shell.

- [ ] **Step 1: Write `App.test.tsx`** to mock `/api/v1/health` and assert the localized shell renders API status.
- [ ] **Step 2: Run:** `cd frontend && npm test -- --run`; expected failure because `App` and client are absent.
- [ ] **Step 3: Implement the typed client and shell:**

```ts
export type HealthResponse = { status: 'UP' };
export async function get<T>(path: string): Promise<T> {
  const response = await fetch(`/api/v1${path}`, { credentials: 'include' });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json() as Promise<T>;
}
```

- [ ] **Step 4: Run:** `cd frontend && npm test -- --run && npm run build`; expected pass.
- [ ] **Step 5: Commit:** `git add frontend && git commit -m "feat: establish frontend foundation"`.

### Task 4: Add local orchestration, tracking, CI, and release artifacts

**Files:**
- Create: `compose.yaml`, `Makefile`, `.tool-versions`
- Create: `scripts/ci/{backend.sh,frontend.sh,e2e.sh,all.sh}`
- Create: `scripts/release/{build-artifacts.sh,verify-reproducibility.sh}`
- Create: `.github/workflows/{ci.yml,release-artifacts.yml}`
- Create: `.github/{ISSUE_TEMPLATE/work-item.yml,PULL_REQUEST_TEMPLATE.md}`
- Create: `docs/project/progress/PROGRESS.md`
- Test: `scripts/ci/workflow-contract.sh`

**Interfaces:**
- Produces: `make test`, `make e2e`, `make artifacts`; `dist/manifest.json` with source revision, checksums, and image digests; local/GitHub cross-links.

- [ ] **Step 1: Write `workflow-contract.sh`** to assert PR/main triggers, Java 21, Node 22, backend/frontend/e2e jobs, artifact dependency on successful CI, no deployment step, and no inline credentials.
- [ ] **Step 2: Run:** `bash scripts/ci/workflow-contract.sh`; expected failure because workflows are absent.
- [ ] **Step 3: Implement workflows and release manifest generation:**

```json
{
  "sourceRevision": "${GITHUB_SHA}",
  "backendSha256": "${BACKEND_SHA256}",
  "frontendSha256": "${FRONTEND_SHA256}",
  "backendImageDigest": "sha256:${BACKEND_IMAGE_DIGEST}",
  "frontendImageDigest": "sha256:${FRONTEND_IMAGE_DIGEST}"
}
```

  Workflow triggers are `pull_request` and pushes to `main`; the release workflow uses `workflow_call`/`workflow_dispatch`, downloads validated outputs, creates OCI archives, and never pushes or deploys.
- [ ] **Step 4: Run:** `bash scripts/ci/workflow-contract.sh && make test && make artifacts`; expected pass with files under ignored `dist/`.
- [ ] **Step 5: Commit:** `git add compose.yaml Makefile .tool-versions scripts .github docs/project/progress && git commit -m "ci: add build-ready delivery pipeline"`.

---

## Milestone 2 — Access, catalog, slots, and discovery

### Task 5: Freeze identity and catalog contracts

**Files:**
- Create: `docs/architecture/adr-002-identity-catalog-search.md`
- Create: `docs/architecture/contracts/m2-catalog.yaml`
- Modify: `docs/api/openapi.yaml`

**Interfaces:**
- Produces: DTOs `RegisterRequest`, `SessionView`, `ShopView`, `ServiceView`, `SlotView`, `SearchPage`; role values `CUSTOMER`, `PROVIDER`, `ADMIN`.

- [ ] **Step 1: Add OpenAPI contract assertions** for ownership, verification prerequisites, public versus authenticated fields, pagination, and errors `400/401/403/409`.
- [ ] **Step 2: Run:** `npx --yes @redocly/cli lint docs/api/openapi.yaml`; expected failure until new schemas and operations are complete.
- [ ] **Step 3: Define operations** under `/api/v1/auth`, `/api/v1/provider/shop`, `/api/v1/provider/services`, `/api/v1/services`, and `/api/v1/services/{id}/slots`, using RFC 9457 problem responses.
- [ ] **Step 4: Run the OpenAPI lint again;** expected pass.
- [ ] **Step 5: Commit:** `git add docs/architecture docs/api/openapi.yaml && git commit -m "docs: freeze catalog contracts"`.

### Task 6: Implement access, catalog, slots, and search backend

**Files:**
- Create: `backend/src/main/java/ch/servicebooking/auth/**`
- Create: `backend/src/main/java/ch/servicebooking/catalog/**`
- Create: `backend/src/main/java/ch/servicebooking/search/**`
- Create: `backend/src/main/java/ch/servicebooking/media/**`
- Create: `backend/src/main/resources/db/migration/V2__identity_catalog.sql`
- Test: `backend/src/test/java/ch/servicebooking/{auth,catalog,search}/**`

**Interfaces:**
- Consumes: milestone-2 OpenAPI contract.
- Produces: application services `AccountService`, `CatalogService`, `SlotService`, `SearchService`; transactional PostgreSQL repositories.

- [ ] **Step 1: Write failing integration tests** for separate roles, verification gates, one shop/provider, postal address, service images, explicit slot times/capacity, publish-time non-overlap, bulk nonrecurring slots, and public search behavior.
- [ ] **Step 2: Run:** `cd backend && ./mvnw -q -Dtest='*Auth*IT,*Catalog*IT,*Search*IT' test`; expected failures for missing endpoints.
- [ ] **Step 3: Implement service boundaries:**

```java
interface CatalogService {
  ShopView saveShop(UUID providerId, SaveShopCommand command);
  ServiceView saveService(UUID providerId, SaveServiceCommand command);
  List<SlotView> addSlots(UUID providerId, UUID serviceId, List<CreateSlotCommand> slots);
  ServiceView publish(UUID providerId, UUID serviceId);
}

interface SearchService {
  Page<ServiceSummary> search(SearchQuery query, Pageable page);
}
```

  Use BCrypt passwords, JDBC-backed sessions, CSRF protection, `Europe/Zurich` parsing to UTC, `unaccent` plus `pg_trgm`, quoted exact phrases, fixed category seeds, and database overlap checks at publish.
- [ ] **Step 4: Run:** `cd backend && ./mvnw -q test`; expected pass.
- [ ] **Step 5: Commit:** `git add backend && git commit -m "feat: add catalog and discovery api"`.

### Task 7: Implement access, catalog, slots, and search frontend

**Files:**
- Create: `frontend/src/features/{auth,provider,services,search}/**`
- Create: `frontend/src/i18n/{index.ts,en.ts,de.ts}`
- Modify: `frontend/src/app/{App.tsx,router.tsx}` and `frontend/src/styles.css`
- Test: `frontend/src/features/**/*.test.tsx`

**Interfaces:**
- Consumes: milestone-2 OpenAPI operations.
- Produces: routes `/`, `/sign-in`, `/register/customer`, `/register/provider`, `/provider/shop`, `/provider/services`, `/services/:id`.

- [ ] **Step 1: Write failing component tests** for public search, exact aggregate inventory without public slot times, provider publication, verification prompts, language switch, labeled original/manual content variants, and mobile navigation.
- [ ] **Step 2: Run:** `cd frontend && npm test -- --run`; expected failures for absent routes/components.
- [ ] **Step 3: Implement typed feature clients and routes.** Manual translations render as labeled variants without automatic interface-language selection:

```ts
export type LocalizedText = { language: 'en' | 'de'; value: string };
export type ServiceSummary = {
  id: string; name: LocalizedText[]; price: string; currency: 'CHF';
  availableInventory: number;
};
```

- [ ] **Step 4: Run:** `cd frontend && npm test -- --run && npm run build`; expected pass at `390px` and desktop component viewports.
- [ ] **Step 5: Commit:** `git add frontend && git commit -m "feat: add catalog discovery experience"`.

---

## Milestone 3 — Reservations, checkout, and orders

### Task 8: Freeze commerce contracts

**Files:**
- Create: `docs/architecture/adr-003-inventory-checkout.md`
- Create: `docs/architecture/contracts/m3-commerce.yaml`
- Modify: `docs/api/openapi.yaml`

**Interfaces:**
- Produces: `CartView`, `CartItemView`, `CheckoutQuote`, `PaymentAttemptView`, `OrderView`; `Idempotency-Key` requirement on checkout.

- [ ] **Step 1: Add contract cases** for live cart repricing, explicit quote acceptance, attempt price snapshot, selected-item atomicity, failed-payment retention, and one multi-provider order.
- [ ] **Step 2: Run OpenAPI lint;** expected failure until all commerce schemas are referenced.
- [ ] **Step 3: Define commerce operations** under `/api/v1/cart`, `/api/v1/checkout/quote`, `/api/v1/checkout/pay`, and `/api/v1/orders`, including conflict responses.
- [ ] **Step 4: Run OpenAPI lint;** expected pass.
- [ ] **Step 5: Commit:** `git add docs/architecture docs/api/openapi.yaml && git commit -m "docs: freeze commerce contracts"`.

### Task 9: Implement reservations, checkout, and order backend

**Files:**
- Create: `backend/src/main/java/ch/servicebooking/cart/**`
- Create: `backend/src/main/java/ch/servicebooking/checkout/**`
- Create: `backend/src/main/java/ch/servicebooking/order/**`
- Create: `backend/src/main/resources/db/migration/V3__commerce.sql`
- Test: `backend/src/test/java/ch/servicebooking/{cart,checkout,order}/**`

**Interfaces:**
- Produces: `CartService`, `CheckoutService`, `OrderQueryService`, `PaymentGateway` and `SimulatedPaymentGateway`.

- [ ] **Step 1: Write failing transactional tests** for immediate reservation, quantity edits/removal, cross-device cart persistence, selected checkout, provider price changes, payment snapshots, failure retry, idempotency replay, and concurrent oversell prevention.
- [ ] **Step 2: Run:** `cd backend && ./mvnw -q -Dtest='*Cart*IT,*Checkout*IT,*Order*IT' test`; expected failures.
- [ ] **Step 3: Implement commands and locking:**

```java
interface CheckoutService {
  CheckoutQuote quote(UUID customerId, Set<UUID> cartItemIds);
  PaymentResult pay(UUID customerId, UUID quoteId, PaymentSimulation simulation, String idempotencyKey);
}

enum PaymentSimulation { SUCCEED, FAIL }
```

  Lock selected slots/cart rows in stable UUID order; compute available capacity as capacity minus active cart reservations minus purchased units; persist accepted quote lines and the payment-attempt snapshot; create one order only on success.
- [ ] **Step 4: Run:** `cd backend && ./mvnw -q test`; expected pass, including concurrent Testcontainers tests.
- [ ] **Step 5: Commit:** `git add backend && git commit -m "feat: add cart checkout and orders"`.

### Task 10: Implement cart, checkout, and order frontend

**Files:**
- Create: `frontend/src/features/{cart,checkout,orders}/**`
- Modify: `frontend/src/app/router.tsx`
- Test: `frontend/src/features/{cart,checkout,orders}/**/*.test.tsx`

**Interfaces:**
- Consumes: commerce API.
- Produces: routes `/cart`, `/checkout`, `/orders`, `/orders/:id`; explicit simulated success/failure control.

- [ ] **Step 1: Write failing tests** for one active cart, direct quantity edits, selected checkout, CHF totals, changed-total consent, payment failure retention, and immutable ordered prices.
- [ ] **Step 2: Run:** `cd frontend && npm test -- --run`; expected failures.
- [ ] **Step 3: Implement commerce state with server-authoritative queries:**

```ts
export type CheckoutQuote = {
  quoteId: string;
  lines: Array<{ cartItemId: string; quantity: number; unitPrice: string }>;
  total: string;
  currency: 'CHF';
};
```

  Require an explicit acceptance checkbox whenever the server quote differs from the previously displayed cart total.
- [ ] **Step 4: Run:** `cd frontend && npm test -- --run && npm run build`; expected pass.
- [ ] **Step 5: Commit:** `git add frontend && git commit -m "feat: add cart checkout and order ui"`.

---

## Milestone 4 — Fulfillment, administration, and release candidate

### Task 11: Freeze fulfillment and administration contracts

**Files:**
- Create: `docs/architecture/adr-004-fulfillment-administration.md`
- Create: `docs/architecture/contracts/m4-fulfillment.yaml`
- Modify: `docs/api/openapi.yaml`

**Interfaces:**
- Produces: `BookingLineView`, `RedemptionResult`, `NotificationView`, `AdminReservationView`; states `AWAITING_FULFILLMENT`, `DELIVERED`, `EXPIRED`, `COMPLETED`.

- [ ] **Step 1: Write contract cases** for early redemption, single-use code, slot-end expiry, Completed aggregation, unpublication/suspension preservation, cart release, and Expired-to-Delivered administrator override.
- [ ] **Step 2: Run OpenAPI lint;** expected failure until fulfillment/admin operations are complete.
- [ ] **Step 3: Define fulfillment operations** for provider, customer, and administrator views, with no refund, messaging, cancellation, rescheduling, timer, or deletion routes.
- [ ] **Step 4: Run OpenAPI lint;** expected pass.
- [ ] **Step 5: Commit:** `git add docs/architecture docs/api/openapi.yaml && git commit -m "docs: freeze fulfillment contracts"`.

### Task 12: Implement fulfillment and administration backend

**Files:**
- Create: `backend/src/main/java/ch/servicebooking/{redemption,expiry,admin,notification,lifecycle}/**`
- Create: `backend/src/main/resources/db/migration/V4__fulfillment.sql`
- Test: `backend/src/test/java/ch/servicebooking/{redemption,expiry,admin,lifecycle}/**`

**Interfaces:**
- Produces: `RedemptionService`, `ExpiryService`, `ProviderLifecycleService`, `AdministrationService`, `NotificationPort`, `SimulatedNotificationPort`.

- [ ] **Step 1: Write failing tests** for booking selection before code entry, pre-start delivery, same-SKU atomic quantities, immediate code invalidation, expiry at end, post-expiry rejection, Completed aggregation, unpublication, suspension, and admin actions.
- [ ] **Step 2: Run:** `cd backend && ./mvnw -q -Dtest='*Redemption*IT,*Expiry*IT,*Admin*IT,*Lifecycle*IT' test`; expected failures.
- [ ] **Step 3: Implement the state services:**

```java
interface RedemptionService {
  BookingLineView redeem(UUID providerId, UUID bookingLineId, String fourDigitCode);
}

interface AdministrationService {
  void releaseCartQuantity(UUID administratorId, UUID cartItemId);
  BookingLineView markExpiredDelivered(UUID administratorId, UUID bookingLineId);
  void suspendProvider(UUID administratorId, UUID providerId);
}
```

  Derive codes from a server secret plus booking-line ID and validate in constant time; schedule expiry and also reconcile on reads/mutations so delayed jobs cannot expose stale state.
- [ ] **Step 4: Run:** `cd backend && ./mvnw -q test`; expected pass.
- [ ] **Step 5: Commit:** `git add backend && git commit -m "feat: add fulfillment and administration"`.

### Task 13: Implement fulfillment and administration frontend

**Files:**
- Create: `frontend/src/features/{fulfillment,admin,notifications}/**`
- Modify: `frontend/src/features/orders/**` and `frontend/src/app/router.tsx`
- Test: `frontend/src/features/{fulfillment,admin,notifications}/**/*.test.tsx`

**Interfaces:**
- Consumes: milestone-4 API.
- Produces: `/provider/bookings`, `/admin/providers`, `/admin/reservations`, customer line-status and simulated-notification views.

- [ ] **Step 1: Write failing tests** for provider-only lines/customer contact, code entry, Delivered/Expired labels, Completed order, administrator suspension/release/override, and absence of excluded actions.
- [ ] **Step 2: Run:** `cd frontend && npm test -- --run`; expected failures.
- [ ] **Step 3: Implement accessible responsive views** with explicit confirmation for administrative mutations and localized status labels:

```ts
export type BookingStatus = 'AWAITING_FULFILLMENT' | 'DELIVERED' | 'EXPIRED';
export type OrderStatus = 'AWAITING_FULFILLMENT' | 'COMPLETED';
```

- [ ] **Step 4: Run:** `cd frontend && npm test -- --run && npm run build`; expected pass.
- [ ] **Step 5: Commit:** `git add frontend && git commit -m "feat: add fulfillment and admin ui"`.

### Task 14: Complete browser acceptance, tracking, and release evidence

**Files:**
- Create: `e2e/{package.json,package-lock.json,playwright.config.ts}`
- Create: `e2e/tests/{catalog,commerce,fulfillment,admin,mobile}.spec.ts`
- Create: `e2e/fixtures/{accounts.ts,api.ts}`
- Modify: `scripts/ci/e2e.sh`, `.github/workflows/{ci.yml,release-artifacts.yml}`
- Modify: `docs/project/progress/{PROGRESS.md,github-sync.yaml}`
- Create: `docs/project/release/artifact-manifest.schema.json`

**Interfaces:**
- Consumes: all approved journeys and APIs.
- Produces: Playwright HTML/JUnit reports, exact candidate manifest, local/GitHub evidence links, checksummed backend/frontend/OCI artifacts.

- [ ] **Step 1: Write failing Playwright journeys** for provider publication, public search, verified cart/checkout, payment failure/retry, redemption/expiry, administration, and mobile widths.
- [ ] **Step 2: Run:** `make e2e`; expected failures until fixtures and full workflows are wired.
- [ ] **Step 3: Implement acceptance infrastructure** with fixtures, deterministic test-clock hooks restricted to the test profile, trace/video-on-first-retry, workflow report upload, and artifact-manifest validation.
- [ ] **Step 4: Run exact candidate verification:**

```bash
make clean
make test
make e2e
make artifacts
bash scripts/release/verify-reproducibility.sh
```

  Expected: all commands pass; no refund, messaging, cancellation, rescheduling, timer, account-delete, real payment, or deployment path exists.
- [ ] **Step 5: Reconcile local/GitHub tracking** using stable milestone/task IDs, redacted evidence links, and current status; keep local records authoritative.
- [ ] **Step 6: Commit:** `git add e2e scripts .github docs/project && git commit -m "test: complete phase one acceptance evidence"`.

## Gate sequence for every milestone

1. Implementers self-verify their owned task workspaces.
2. `code-reviewer-001` reviews the exact integrated candidate; findings return through the Orchestrator.
3. `build-manager-001` reproduces builds and supply-chain evidence without mutating the candidate.
4. `quality-engineer-001` verifies the supported blast radius on the build-verified snapshot.
5. `independent-auditor-001` audits traceability and evidence only to the Orchestrator.
6. The Orchestrator presents the exact milestone review digest to the application owner.

## Plan self-review

- Spec coverage: all 16 functional and 8 non-functional requirements appear in the validated milestone DAG and one or more tasks above.
- Deferred details: handled only by the explicit minimal defaults in this plan; no deferred feature is added.
- Type consistency: API names, role/status enums, price/inventory ownership, and task dependencies are consistent across milestones.
- Placeholder scan: no implementation placeholder is used; every task names its files, interfaces, failing verification, implementation boundary, passing command, and commit.
