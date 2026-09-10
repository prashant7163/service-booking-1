# Milestone 1 Integration Test Plan

All evidence must bind to the exact candidate revision.

1. Backend foundation: compile and run Spring Boot tests; start an isolated PostgreSQL through Testcontainers; apply Flyway migrations; verify the API health response and structured failure contract.
2. Frontend foundation: run type checking, linting, Vitest, and Testing Library checks; build the production bundle; verify the shell consumes only the configured API base URL.
3. Browser smoke: start the built backend and frontend with synthetic configuration, then use Playwright to verify the responsive shell and backend health integration. This milestone creates the browser-test harness; complete phase-one journeys remain milestone 4 exit evidence.
4. Local orchestration: start PostgreSQL with Docker Compose, verify health, run backend/frontend validation, and stop cleanly.
5. CI policy: validate pull-request and main triggers, least-privilege permissions, cache/lockfile use, failure propagation, report retention, and release-stage dependency on successful validation.
6. Release reproducibility: build backend/frontend archives and container images for one source revision twice, compare normalized payload checksums, and verify the manifest records toolchain inputs, source revision, test evidence, and image digests.
7. Negative gates: a deliberately failing backend test and a deliberately failing Playwright test must each prevent release production.
