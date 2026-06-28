# LangGraph Workflow

InsightAI uses `backend/app/ai/langgraph_workflow.py` to coordinate a
multi-agent analytics workflow. The graph has a deterministic fallback path, so
local development and CI can run without external model credentials.

## Agent sequence

1. Supervisor initializes trace state, retry policy, memory scope, and provider
   mode.
2. Intent Classification detects analytics, dashboard, report, import,
   connector, forecast, comparison, collaboration, and root-cause requests.
3. Workflow Planner chooses agent order, fallback path, retry behavior, and
   approval gates.
4. Model Router selects deterministic fallback or OpenAI-backed routing.
5. Schema Intelligence and Semantic Layer normalize technical schema into
   business terms and governed metrics.
6. Business Context and RAG Knowledge enrich the request with glossary and
   workspace knowledge.
7. Data Quality and Data Lineage identify issues, freshness gaps, dependencies,
   downstream dashboards, reports, and KPIs.
8. Clarification blocks ambiguous requests before generation.
9. SQL Generation or MongoDB Query creates read-only query plans.
10. Query Validation and Query Optimization enforce safety, limits, and cost
    hints.
11. Insight, Executive Decision, Anomaly, Root Cause, Forecasting,
    Visualization, Dashboard Builder, and Report Writer produce the final
    business output.
12. Collaboration, Policy Governance, Security Compliance, Cost Governance,
    Scheduling, Monitoring, and Explanation finalize the response and trace.

## Safety behavior

- SQL generation is validated by `app/security/query_safety.py`.
- MongoDB aggregation blocks mutating stages such as `$merge` and `$out`.
- Clarification can stop the graph before any query is generated.
- Agent errors are captured in `agent_trace`; failed nodes retry according to
  the agent spec.
- The final response includes confidence, trace ID, token usage, query safety
  status, and recommendations.

## Observability

Agent traces are stored in MongoDB and surfaced through:

- `GET /api/v1/admin/agents`
- `GET /api/v1/admin/agents/traces`
- `GET /api/v1/observability/metrics`
- `GET /api/v1/observability/prometheus`
