# InsightAI Agent Architecture

Date: 2026-06-27

## Overview

InsightAI uses a LangGraph `StateGraph` supervised workflow. The Supervisor orchestrates execution, while the Workflow Planner decides agent order, fallback path, retry plan, and approval gates. The graph shares `InsightAIState`, records every agent invocation, persists traces to MongoDB, and routes dynamically based on user intent, model route, ambiguity, source refresh needs, semantic metrics, RAG context, data lineage, anomaly severity, report requirements, collaboration controls, governance, scheduling, monitoring, and security checks.

## Supervisor Flow

1. Supervisor Agent
2. Intent Classification Agent
3. Workflow Planner Agent
4. Model Router Agent
5. Schema Intelligence Agent
6. Semantic Layer Agent
7. Business Context Agent
8. RAG Knowledge Agent
9. Data Quality Agent
10. Data Lineage Agent
11. Enterprise API Integration Agent, when API refresh or SaaS context is required
12. Data Ingestion / ETL Agent, when import/upload/sync intent is detected
13. Clarification Agent
14. SQL Generation Agent or MongoDB Query Agent
15. Query Validation Agent
16. Query Optimization Agent
17. Query Execution Agent
18. Insight Generation Agent
19. Executive Decision Agent
20. Anomaly Detection Agent
21. Root Cause Analysis Agent, when required
22. Forecasting Agent
23. Visualization Agent
24. Dashboard Builder Agent
25. Report Writer Agent
26. Memory Agent
27. Recommendation Agent
28. Collaboration Agent
29. Policy / Governance Agent
30. Security & Compliance Agent
31. Cost Governance Agent
32. Scheduling Agent
33. Monitoring + Observability Agent
34. Explanation Agent

## Enterprise Agents

### Enterprise API Integration Agent

Responsibilities:

- Discover APIs and SaaS platforms
- Validate credential workflow metadata
- Fetch REST data through integration service
- Handle pagination metadata
- Retry failures
- Track incremental sync cursors
- Detect schema through JSON sampling
- Respect rate-limit metadata
- Prepare OAuth refresh hooks

Priority connector support:

- PostgreSQL
- MongoDB
- CSV and Excel
- REST API
- GitHub
- Stripe
- Google Analytics 4

### Enterprise ETL Agent

Responsibilities:

- CSV and JSON import
- Excel/Parquet scheduled-processing placeholders
- REST API ingestion handoff
- Database sync metadata
- Incremental loading and CDC architecture hooks
- Transformation, cleaning, deduplication, and schema mapping

### Executive Decision Agent

Responsibilities:

- Executive summary
- Business risks
- Growth opportunities
- Department performance
- Financial impact
- Customer trends
- Operational issues
- Strategic recommendations
- Priority actions
- Confidence score
- Action plan

### Semantic Layer Agent

Responsibilities:

- Load governed workspace metrics
- Match question terms to semantic definitions
- Share formulas with query, insight, report, and explanation agents
- Prevent repeated metric inference

### Data Lineage Agent

Responsibilities:

- Track source, transformation, and destination
- Identify affected dashboards, reports, and KPIs
- Generate dependency graph metadata
- Generate column-level lineage
- Capture SQL lineage
- Record transformation history
- Produce dashboard/report impact analysis

### Collaboration Agent

Responsibilities:

- Coordinate comments, mentions, shared dashboards, shared reports, activity feed, approvals, and human-in-the-loop controls

### Scheduling Agent

Responsibilities:

- Plan daily, weekly, monthly, and manual scheduled reports
- Attach delivery channels and failure recovery policy
- Prepare alert metadata

### Workflow Planner Agent

Responsibilities:

- Decide which agents run
- Decide order
- Select fallback path
- Select retry plan
- Define human approval gates

### Model Router Agent

Responsibilities:

- Route cheap tasks to cheap model tier
- Route SQL, reasoning, and executive analysis to strong model tier
- Use deterministic fallback in local/test mode

### Policy / Governance Agent

Responsibilities:

- Check PII access
- Check data residency
- Check compliance rules
- Check forbidden datasets
- Check retention policy
- Check approval requirements

### Monitoring + Observability Agent

Responsibilities:

- Track agent spans
- Track trace IDs
- Track latency
- Track token usage
- Track prompt version
- Track tool calls
- Track retries
- Track cost
- Track failure reasons

## Trace Persistence

Every workflow trace includes:

- Execution order
- Workflow plan
- Model route
- Latency
- Token estimates
- Retries
- Errors
- Success status
- Final confidence
- Data quality output
- Semantic layer output
- Data lineage output
- Anomaly output
- ETL output
- API integration output
- Executive decision output
- Collaboration output
- Policy/governance output
- Scheduling output
- Monitoring output
- Cost governance output
- RAG context

Traces are visible in `/admin/agents`.
