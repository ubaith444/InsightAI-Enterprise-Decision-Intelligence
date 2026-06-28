# InsightAI Semantic Layer

Date: 2026-06-27

## Summary

InsightAI V3 includes a workspace-scoped Business Semantic Layer. Administrators can define business metrics once, and the multi-agent workflow consumes those definitions instead of repeatedly inferring business meaning.

## Default Metrics

- Revenue
- Profit
- Gross Margin
- Net Margin
- MRR
- ARR
- Customer Lifetime Value
- Customer Acquisition Cost
- Churn
- Retention
- Inventory Turnover
- Conversion Rate
- Average Order Value
- Return Rate
- Active customer
- Churned customer
- High-value customer
- Monthly recurring revenue

## APIs

- `GET /api/v1/resources/semantic-layer?workspace_id=...`
- `POST /api/v1/resources/semantic-metrics`
- `GET /api/v1/resources/semantic-metrics?workspace_id=...`

## Frontend

The `/semantic` page lists governed metrics and allows Admin/Super Admin users to add new metrics.

## Agent Integration

The Semantic Layer Agent runs after Schema Intelligence and before Data Quality. It adds semantic formulas and matched metrics to shared graph state so query generation, validation, insight, executive decision, report, and explanation agents use the same governed definitions.
