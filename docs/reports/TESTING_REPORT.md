# InsightAI Testing Report

Date: 2026-06-27

## Test Matrix

| Area | Command | Result |
| --- | --- | --- |
| Backend unit/API/integration | `python -m pytest` | Passed: 28 tests |
| Frontend smoke/typecheck | `npm.cmd run test` | Passed |
| Frontend production build | `npm.cmd run build` | Passed |
| Browser E2E | `npm.cmd run test:e2e` | Passed: 2 tests |
| Frontend dependency audit | `npm.cmd audit --audit-level=moderate` | Passed: 0 vulnerabilities |

## Backend Coverage

- Authentication and demo login.
- Workspace creation and isolation.
- Database connection creation with encrypted URI storage and masked API responses.
- Demo schema includes Sales, Customers, Products, Orders, Employees, Regions, Expenses, and Inventory.
- Schema intelligence includes primary keys, foreign keys, relationships, column meanings, metric definitions, and business glossary.
- AI ask flow returns query confidence, insights, rows, charts, and agent trace.
- Clarification flow blocks vague prompts before query generation.
- Query safety blocks mutating SQL and unsafe MongoDB stages.
- Celery/Redis async job path returns job status in local eager mode.
- Workspace resource APIs cover glossary, saved prompts, scheduled reports, exports, source health, and usage analytics.
- RAG knowledge APIs cover PDFs, SOPs, policies, contracts, and meeting notes.
- RBAC restrictions for Viewer and Analyst roles.
- Admin analytics and audit log access.

## Frontend Coverage

- TypeScript smoke check for all app routes.
- Production build for 27 app routes, including `/integrations`, `/realtime`, `/semantic`, `/lineage`, `/collaboration`, and `/admin/agents`.
- Playwright E2E for register/login, create connection, load schema, ask AI question, render chart, save dashboard, report download/export flow, history, admin gating, and clarification prompt.

## Bugs Found and Fixed During This Pass

- Expanded chart recommendations returned `map` and `kpi`, while older tests only allowed legacy chart types. Tests were updated to match the product feature.
- Product tests initially selected the newest workspace rather than the seeded demo workspace. Helpers now select the `acme-revenue` demo workspace explicitly.
- Frontend typecheck failed on billing metric tuple inference. Billing page tuple typing was tightened.
- Running `npm.cmd run test` concurrently with `next build` caused a transient `.next/types` route-generation race. Re-running typecheck after build passed.
- Playwright exposed stale report export placeholder copy. Reports now use authenticated backend download actions, and the E2E verifies PDF download behavior.
- V3 contract changes required tests to expect `scheduled` scheduled-report records and the 32-agent registry.

## Security Validation

Passed for tested scope.

- New database connection strings are encrypted at rest.
- Credentials are masked in API/frontend responses.
- AI queries are rate-limited by user/workspace.
- AI question input is sanitized.
- SQL execution is read-only with default limits.
- MongoDB aggregation blocks write stages.
- Workspace access checks protect resource, query, dashboard, report, connection, and admin-adjacent routes.
- Semantic metrics, data lineage, comments, activity feed, approvals, and settings are workspace-scoped.
- Final architecture tests cover Workflow Planner, Model Router, early RAG routing, Policy/Governance, Monitoring + Observability, Excel import, GitHub REST sync, report downloads, dashboard export, settings persistence, realtime snapshot, and WebSocket live updates.
- Human-in-the-loop approval records are required for publishing, report sending, external actions, dataset deletion, and destructive operations.
- Audit logs are append-only through service usage.

## Final Status

All requested validation commands passed after fixes.

Production readiness score: 9/10.
