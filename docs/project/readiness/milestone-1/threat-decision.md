# Milestone 1 Threat Decision

Milestone 1 establishes the controls needed by later product milestones and must not weaken the approved threat model.

- Browser-to-API: one versioned API base path, structured errors, explicit CORS/runtime configuration, and no secret-bearing client configuration.
- API-to-PostgreSQL: migrations are versioned, tests use isolated PostgreSQL, credentials come from environment configuration, and synthetic data is used locally.
- Identity and ownership: Spring Security seams and roles are established in the backend boundary; authorization is server-side. Product endpoints arrive in later milestones.
- Inventory and checkout: later persistence APIs must support atomic reservation/checkout invariants; milestone 1 must avoid an architecture that requires client-authoritative inventory.
- CI: pull-request code receives least-privilege permissions, no publishing credentials, and failed required tests block release production.
- Release: artifacts bind to an exact source revision and successful validation; deployment and registry publication remain disabled.
- Tracking: local stable IDs remain authoritative; GitHub failures create retryable local state and cannot imply approval.

Residual risks remain as approved in the specification, including abandoned-cart inventory hoarding and the need for a production security/retention review before real-user deployment.
