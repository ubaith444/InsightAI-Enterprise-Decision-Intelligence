# Performance Guide

InsightAI performance depends on API latency, database query cost, LangGraph
agent count, token usage, frontend rendering, and background job throughput.

## Backend targets

| Area | Target |
| --- | --- |
| Health endpoint | < 100 ms |
| Cached schema inspection | < 500 ms |
| AI query generation in mock mode | < 2 seconds |
| Safe query execution on demo data | < 2 seconds |
| Report export job enqueue | < 500 ms |

## Controls

- `DEFAULT_QUERY_LIMIT` limits rows returned by generated queries.
- `QUERY_TIMEOUT_SECONDS` caps query execution time.
- Query safety rejects mutating statements and multiple SQL statements.
- Cost governance records token usage, estimated AI cost, row count, and query
  cost score.
- Celery can move long-running reports, imports, and scheduled sync work out of
  request/response paths.

## Frontend practices

- Keep dashboard widgets bounded and paginated.
- Use TanStack Query caching for API state.
- Prefer server-side filtering for large datasets.
- Keep chart datasets summarized before rendering.
- Use Playwright smoke flows after significant UI or routing changes.

## Observability

Use these endpoints to inspect behavior:

- `GET /api/v1/observability/metrics`
- `GET /api/v1/observability/prometheus`
- `GET /api/v1/admin/agents/traces`
- `GET /api/v1/resources/usage/analytics`
