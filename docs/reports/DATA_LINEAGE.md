# InsightAI Data Lineage

Date: 2026-06-27

## Summary

InsightAI V3 tracks lineage across sources, transformations, semantic KPIs, dashboards, reports, and generated AI workflows. Lineage is available through a backend API, a frontend Data Lineage page, and persisted agent trace outputs.

## API

- `GET /api/v1/resources/data-lineage?workspace_id=...`

## Lineage Output

```json
{
  "workspace_id": "workspace-id",
  "nodes": [],
  "edges": [],
  "affected_dashboards": [],
  "affected_reports": [],
  "affected_kpis": [],
  "column_level_lineage": [],
  "sql_lineage": [],
  "transformation_history": [],
  "impact_analysis": {},
  "generated_at": "2026-06-27T00:00:00"
}
```

## Agent Output

The Data Lineage Agent returns:

- Source
- Transformation
- Destination
- Affected dashboards
- Affected reports
- Affected KPIs
- Column-level lineage
- SQL lineage
- Transformation history
- Dashboard/report impact analysis
- Dependency graph

## Frontend

The `/lineage` page displays dependency counts, KPI coverage, graph edges, and source/dashboard/report assets.

## Remaining Production Work

For large deployments, lineage can be further augmented with warehouse query plans, dbt metadata, BI tool metadata, and column-level lineage from production catalog systems.
