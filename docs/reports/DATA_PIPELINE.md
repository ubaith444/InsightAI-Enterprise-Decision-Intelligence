# InsightAI Data Pipeline

Date: 2026-06-27

## Summary

InsightAI V3 supports live operational data through database connectors, REST API sync metadata, CSV/JSON ETL imports, workspace semantic metrics, data quality checks, lineage graph generation, realtime analytics, and downstream dashboard/report outputs.

## Pipeline Flow

1. Source connection or file/API import is created within a workspace.
2. Credentials are encrypted or kept outside frontend responses.
3. Schema is read and converted into schema intelligence.
4. Semantic Layer Agent enriches the workflow with governed metric definitions.
5. Data Quality Agent scores completeness, duplicates, invalid dates, freshness, relationships, and outliers.
6. Query agents generate and validate safe read-only SQL or MongoDB aggregation.
7. Execution returns rows and logs query metadata.
8. Result agents create insights, anomalies, executive decisions, charts, dashboards, reports, lineage, collaboration metadata, and monitoring output.
9. Realtime APIs stream workspace KPIs and recent query activity.

## Realtime Interfaces

- `GET /api/v1/realtime/snapshot?workspace_id=...`
- `GET /api/v1/realtime/events?workspace_id=...`
- `WS /api/v1/realtime/ws/{workspace_id}`

## Batch and Async Interfaces

- Celery task: `insightai.execute_query`
- Redis broker/result backend in production mode
- ETL route: `POST /api/v1/enterprise/etl/import`
- Sync route: `POST /api/v1/enterprise/api/sync`

## Future Kafka Path

Kafka can be introduced behind the current realtime contract for query events, ETL events, source sync events, report completion, anomaly alerts, and workflow traces without changing frontend API calls.
