# InsightAI Observability Guide

Date: 2026-06-27

## Implemented Observability

- Request metrics middleware
- JSON metrics endpoint
- Prometheus text endpoint
- Health endpoint
- Agent trace persistence
- Execution timeline
- Latency
- Retries
- Errors
- Success rate
- Confidence score
- Token usage
- Cost governance output
- Monitoring + Observability Agent output
- Agent spans
- Prompt version
- Tool calls
- Cost
- Failure reasons

## Endpoints

- `GET /health`
- `GET /api/v1/observability/metrics`
- `GET /api/v1/observability/prometheus`
- `GET /api/v1/admin/agents`
- `GET /api/v1/admin/agents/traces?workspace_id=...`

## Admin Dashboard

The `/admin/agents` page displays 35 registered agents, workflow count, success rate, execution timeline, latency, retries, token usage, cost score, quality score, anomaly severity, executive confidence, semantic metrics, lineage KPIs, approval gate status, planner readiness, model route, governance decision, and monitoring health.

## Grafana Path

Use `/api/v1/observability/prometheus` as a scrape target through Prometheus. Recommended dashboards:

- API request volume by path
- API latency by path
- Error rate
- Workflow success rate
- Agent latency
- Token usage
- Query cost score
- Data quality score

## OpenTelemetry Path

The Monitoring + Observability Agent emits an `otel_trace_id` matching the workflow trace ID and agent spans for every agent invocation. Production OpenTelemetry exporters can attach this ID to FastAPI middleware, Celery tasks, database spans, and external connector calls.
