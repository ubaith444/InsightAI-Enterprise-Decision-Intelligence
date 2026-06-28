# InsightAI API Routes

Date: 2026-06-27

Base API prefix: `/api/v1`

## Health

- `GET /health`
  - Returns API status and environment validation.

## Auth and Users

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/users/me`

## Workspaces

- `GET /api/v1/workspaces`
- `POST /api/v1/workspaces`

## Database Connections

- `GET /api/v1/connections?workspace_id=...`
- `POST /api/v1/connections`
- `POST /api/v1/connections/{connection_id}/test`
- `GET /api/v1/connections/{connection_id}/schema`
- `GET /api/v1/schema?connection_id=...`

Security:

- Connection strings are encrypted at rest for new connections.
- API responses expose only `masked_uri`.
- Workspace access is enforced before connection access.

## AI

- `POST /api/v1/ai/ask`
- `POST /api/v1/ai/validate`

AI responses include:

- Generated SQL or MongoDB aggregation
- Safety result
- Table rows
- Insights
- Chart recommendation
- Agent trace
- Final confidence
- Query confidence object with score, reasoning, risk, and corrections

## Queries

- `GET /api/v1/queries/history?workspace_id=...`
- `POST /api/v1/queries/execute`
- `GET /api/v1/queries/jobs/{job_id}`

Async jobs use Celery + Redis in production mode.

## Dashboards

- `GET /api/v1/dashboards?workspace_id=...`
- `POST /api/v1/dashboards`
- `PUT /api/v1/dashboards/{dashboard_id}`
- `DELETE /api/v1/dashboards/{dashboard_id}?workspace_id=...`
- `POST /api/v1/dashboards/{dashboard_id}/duplicate?workspace_id=...`
- `GET /api/v1/dashboards/{dashboard_id}/export?workspace_id=...&format=csv|excel|pdf|powerpoint`

## Reports

- `GET /api/v1/reports?workspace_id=...`
- `POST /api/v1/reports`
- `PUT /api/v1/reports/{report_id}`
- `GET /api/v1/reports/{report_id}/download?workspace_id=...&format=csv|excel|pdf|powerpoint`

## Enterprise Connectors and ETL

- `GET /api/v1/enterprise/connectors/catalog`
- `POST /api/v1/enterprise/api/test`
- `POST /api/v1/enterprise/api/sync`
- `GET /api/v1/enterprise/api/sync-history?workspace_id=...`
- `POST /api/v1/enterprise/etl/import`
- `GET /api/v1/enterprise/etl/runs?workspace_id=...`

Implemented live paths include REST API test/sync and CSV/JSON ETL import with validation, cleaning, deduplication, and persisted run history.

## Realtime and Observability

- `GET /api/v1/realtime/snapshot?workspace_id=...`
- `GET /api/v1/realtime/events?workspace_id=...`
- `WS /api/v1/realtime/ws/{workspace_id}`
- `GET /api/v1/observability/metrics`
- `GET /api/v1/observability/prometheus`

## Workspace Resources

- `GET /api/v1/resources/business-glossary?workspace_id=...`
- `GET /api/v1/resources/semantic-layer?workspace_id=...`
- `POST /api/v1/resources/semantic-metrics`
- `GET /api/v1/resources/semantic-metrics?workspace_id=...`
- `GET /api/v1/resources/data-lineage?workspace_id=...`
- `GET /api/v1/resources/comments/list?workspace_id=...`
- `POST /api/v1/resources/comments`
- `GET /api/v1/resources/activity-feed?workspace_id=...`
- `POST /api/v1/resources/activity`
- `GET /api/v1/resources/approvals/list?workspace_id=...`
- `POST /api/v1/resources/approvals`
- `GET /api/v1/resources/saved-prompts?workspace_id=...`
- `GET /api/v1/resources/knowledge-documents?workspace_id=...`
- `POST /api/v1/resources/knowledge-documents`
- `POST /api/v1/resources/knowledge-search`
- `GET /api/v1/resources/api-keys?workspace_id=...`
- `GET /api/v1/resources/billing?workspace_id=...`
- `GET /api/v1/resources/team?workspace_id=...`
- `GET /api/v1/resources/workspace-settings?workspace_id=...`
- `GET /api/v1/resources/profile-settings?workspace_id=...`
- `POST /api/v1/resources`
- `PUT /api/v1/resources/{resource_type}/{resource_id}`
- `DELETE /api/v1/resources/{resource_type}/{resource_id}?workspace_id=...`

Generic create payload:

```json
{
  "workspace_id": "workspace-id",
  "resource_type": "saved-prompts",
  "name": "Monthly sales trend",
  "payload": {
    "question": "Show monthly sales trend"
  }
}
```

## Notifications

## RAG Knowledge Search

Knowledge document types:

- `pdf`
- `sop`
- `policy`
- `contract`
- `meeting_note`

Search payload:

```json
{
  "workspace_id": "workspace-id",
  "query": "revenue drop policy meeting notes",
  "document_types": ["pdf", "sop", "policy", "contract", "meeting_note"],
  "limit": 5
}
```

The RAG Knowledge Agent uses the same workspace-scoped search layer and persists retrieved context in `agent_traces.agent_outputs.rag_context`.

- `GET /api/v1/resources/notifications/list?workspace_id=...`
- `POST /api/v1/resources/notifications`

## Scheduled Reports

- `GET /api/v1/resources/scheduled-reports/list?workspace_id=...`
- `POST /api/v1/resources/scheduled-reports`

Supports `daily`, `weekly`, and `monthly` cadence values by convention, with email, WhatsApp, and Slack delivery placeholders.

## Exports

- `GET /api/v1/resources/exports/list?workspace_id=...`
- `POST /api/v1/resources/exports`

Supported formats:

- `csv`
- `excel`
- `pdf` placeholder
- `powerpoint` placeholder

## Source Health

- `GET /api/v1/resources/source-health/list?workspace_id=...`

Returns connection status, last successful sync, last failed query, average response time, and error rate.

## Usage Analytics

- `GET /api/v1/resources/usage/analytics?workspace_id=...`

Tracks AI questions, executed queries, dashboards, reports, token usage, and failed queries.

## Audit Logs

- `GET /api/v1/audit-logs?workspace_id=...`

## Admin

- `GET /api/v1/admin/analytics`
- `GET /api/v1/admin/agents`
- `GET /api/v1/admin/agents/traces?workspace_id=...`

Admin routes require Admin or Super Admin privileges.
