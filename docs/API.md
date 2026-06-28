# InsightAI API

Base URL: `http://127.0.0.1:8000/api/v1`

Authentication uses bearer JWT tokens returned by `POST /auth/login` and
`POST /auth/register`.

## Authentication

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/auth/register` | Create a user, issue a token, and seed the first workspace. |
| POST | `/auth/login` | Email/password login and JWT issue. |
| GET | `/auth/google-placeholder` | OAuth placeholder for future Google sign-in. |

## Users and workspaces

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/users/me` | Current user profile. |
| GET | `/users` | Admin user inventory. |
| GET | `/workspaces` | List workspaces visible to the current user. |
| POST | `/workspaces` | Create a workspace. |

## Connections and schema

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/connections` | List workspace database and API connections. |
| POST | `/connections` | Create a masked read-only connection. |
| POST | `/connections/{connection_id}/test` | Validate connection reachability. |
| GET | `/connections/{connection_id}/schema` | Inspect selected source schema. |
| GET | `/schema` | Explore active demo/workspace schema. |

## AI analytics and query execution

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/ai/ask` | Generate, validate, optionally execute, chart, explain, and audit a question. |
| POST | `/ai/validate` | Validate SQL or MongoDB aggregation safety. |
| GET | `/queries/history` | List query logs. |
| POST | `/queries/execute` | Execute a validated read query. |
| GET | `/queries/jobs/{job_id}` | Inspect async query job status. |

## Dashboards and reports

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/dashboards` | List dashboards. |
| POST | `/dashboards` | Create a dashboard. |
| PUT | `/dashboards/{dashboard_id}` | Update dashboard configuration. |
| DELETE | `/dashboards/{dashboard_id}` | Delete dashboard configuration. |
| POST | `/dashboards/{dashboard_id}/duplicate` | Duplicate a dashboard. |
| GET | `/dashboards/{dashboard_id}/export` | Export dashboard data. |
| GET | `/reports` | List reports. |
| POST | `/reports` | Create a report. |
| PUT | `/reports/{report_id}` | Update a report. |
| GET | `/reports/{report_id}/download` | Download report output. |

## Enterprise resources

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/enterprise/connectors/catalog` | Connector catalog. |
| POST | `/enterprise/api/test` | Test external API connector settings. |
| POST | `/enterprise/api/sync` | Start API sync. |
| GET | `/enterprise/api/sync-history` | API sync history. |
| POST | `/enterprise/etl/import` | CSV/Excel import. |
| GET | `/enterprise/etl/runs` | ETL run history. |
| GET | `/resources/semantic-layer` | Workspace metrics and glossary. |
| POST | `/resources/semantic-metrics` | Create semantic metric. |
| GET | `/resources/data-lineage` | Lineage and impact graph. |
| GET | `/resources/comments/list` | Comments. |
| POST | `/resources/comments` | Create comment. |
| GET | `/resources/activity-feed` | Activity feed. |
| POST | `/resources/activity` | Create activity event. |
| GET | `/resources/approvals/list` | Approval queue. |
| POST | `/resources/approvals` | Create approval request. |
| GET | `/resources/notifications/list` | Notifications. |
| POST | `/resources/notifications` | Create notification. |
| GET | `/resources/scheduled-reports/list` | Scheduled reports. |
| POST | `/resources/scheduled-reports` | Schedule a report. |
| POST | `/resources/exports` | Start export. |
| GET | `/resources/exports/list` | Export history. |
| GET | `/resources/source-health/list` | Source health checks. |
| GET | `/resources/usage/analytics` | Usage analytics. |
| POST | `/resources/knowledge-documents` | Add knowledge document. |
| POST | `/resources/knowledge-search` | Search workspace knowledge. |
| GET | `/resources/{resource_type}` | Generic resource list. |
| POST | `/resources` | Generic resource create. |
| PUT | `/resources/{resource_type}/{resource_id}` | Generic resource update. |
| DELETE | `/resources/{resource_type}/{resource_id}` | Generic resource delete. |

## Realtime, audit, observability, and admin

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/realtime/snapshot` | Current realtime KPI snapshot. |
| GET | `/realtime/events` | Realtime event list. |
| GET | `/audit-logs` | Admin audit events. |
| GET | `/observability/metrics` | JSON metrics snapshot. |
| GET | `/observability/prometheus` | Prometheus text metrics. |
| GET | `/admin/analytics` | Admin analytics, usage, failures, and health. |
| GET | `/admin/agents` | Agent catalog. |
| GET | `/admin/agents/traces` | Recent agent traces. |
| GET | `/health` | Public health check. |

## Safety guarantees

SQL execution accepts only `SELECT` or read-only CTE queries, blocks mutating
keywords, rejects multiple statements, and applies a default `LIMIT`.

MongoDB aggregation blocks write-oriented stages such as `$merge` and `$out`,
then applies a default `$limit` when missing.
