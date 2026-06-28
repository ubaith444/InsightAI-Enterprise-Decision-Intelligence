# InsightAI Performance Report

Date: 2026-06-27

## Summary

Local validation focused on correctness, build integrity, and E2E behavior. The system includes performance-oriented controls for query limits, timeouts, query cost scoring, Redis/Celery async execution, realtime refresh intervals, request latency metrics, and agent-level latency tracking.

## Current Local Evidence

| Check | Result |
| --- | --- |
| Backend tests | Passed: 25 tests |
| Frontend typecheck | Passed |
| Frontend production build | Passed: 27 routes |
| Playwright E2E | Passed: 2 tests |
| npm audit | Passed: 0 vulnerabilities |
| Query timeout metadata | Implemented |
| Query cost score | Implemented |
| Async query job path | Implemented |
| Request latency metrics | Implemented |
| Agent latency metrics | Implemented |

## Performance Controls

- Default SQL and MongoDB result limiting
- Query timeout configuration
- Redis/Celery execution for long-running queries
- Query complexity and cost warnings
- Realtime refresh interval controls: 5s, 15s, 30s, 60s, manual
- Agent token and latency accounting
- Prometheus-compatible metrics endpoint

## Remaining Load Testing Work

The repository is ready for Locust or k6-style load tests, but no production traffic profile has been supplied. Before launch, run load tests against staging with realistic query volume, dashboard refresh patterns, ETL file sizes, and external connector latency.
