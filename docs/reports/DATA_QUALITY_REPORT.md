# InsightAI Data Quality Report

Date: 2026-06-27

## Summary

The Data Quality Agent is part of the LangGraph workflow and runs after Schema Intelligence. It evaluates schema and sample data context before query generation so users can see whether results may be affected by missing values, duplicates, invalid dates, broken relationships, stale data, or outliers.

## Agent Output

```json
{
  "quality_score": 0.91,
  "issues": [
    "freshness_unknown",
    "possible_outliers"
  ],
  "affected_tables": [
    "sales",
    "orders"
  ],
  "recommendations": [
    "Add freshness metadata for source tables",
    "Review high-value revenue rows before executive reporting"
  ]
}
```

## Checks Covered

- Missing values
- Duplicate records
- Invalid dates
- Broken relationship metadata
- Stale data indicators
- Suspicious outliers

## Trace Persistence

Data quality output is persisted in `agent_traces.agent_outputs.data_quality` and displayed in the Admin Agent Monitoring Dashboard. The trace includes invocation order, latency, retry count, token estimate, success status, and quality score.

## Validation

Backend tests cover registration and execution of the Data Quality Agent as part of the multi-agent workflow. Enterprise V2 tests also verify that agent outputs persist into the trace surface consumed by the admin dashboard.

## Remaining Production Work

Live production data quality scoring should be tuned per customer source. Recommended next steps are table-level freshness SLAs, configurable null thresholds, relationship checks against live foreign keys, and anomaly thresholds per metric.
