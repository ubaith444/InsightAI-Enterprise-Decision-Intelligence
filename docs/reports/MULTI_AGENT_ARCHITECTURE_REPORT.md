# InsightAI Multi-Agent Architecture Report

Date: 2026-06-27

## Summary

InsightAI now uses a production-grade LangGraph multi-agent workflow instead of a single query-generation step. The architecture includes a Supervisor Agent, 24 specialized production agents, shared graph state, conditional routing, deterministic/mock fallback behavior, persisted MongoDB workflow traces, agent memory, cost governance, data quality checks, anomaly detection, ETL routing, and an Admin monitoring surface.

## Implemented Agents

| Layer | Agent | Responsibility |
| --- | --- | --- |
| Orchestration | Supervisor Agent | Initializes shared state, provider mode, retries, errors, token tracking, and trace IDs |
| Intent | Intent Classification Agent | Detects analytics, dashboard, report, database, visualization, prediction, comparison, explanation, and root-cause intents |
| Data context | Schema Intelligence Agent | Builds structured schema, relationship, asset, and glossary context |
| Data quality | Data Quality Agent | Detects missing values, duplicate records, invalid dates, broken relationships, stale data, and suspicious outliers |
| Data context | Business Context Agent | Maps business terms like revenue, churn, margin, active customer, and monthly revenue to data fields |
| Ingestion | Data Ingestion / ETL Agent | Supports CSV/Excel upload validation, cleaning, glossary mapping, and scheduled import placeholders |
| Control | Clarification Agent | Stops ambiguous requests and asks a clarification question before query generation |
| Querying | SQL Generation Agent | Generates read-only SQL for analytical requests |
| Querying | MongoDB Query Agent | Generates read-only aggregation pipelines using allowed stages |
| Safety | Query Validation Agent | Validates read-only behavior, syntax, limits, timeout metadata, and isolation context |
| Performance | Query Optimization Agent | Adds execution-plan, index, limit, and retry-policy hints |
| Execution | Query Execution Agent | Defines timeout/retry/pooling behavior used by the service executor |
| Insights | Insight Generation Agent | Produces summaries, findings, anomalies, and recommendations |
| Insights | Anomaly Detection Agent | Detects metric spikes, drops, unusual trends, severity, and next-agent routing |
| Insights | Root Cause Analysis Agent | Adds RCA prompts for drops, spikes, and "why" questions |
| Forecasting | Forecasting Agent | Uses simple statistical moving-average forecasts before AI explanation |
| Visualization | Visualization Agent | Recommends charts and widget types |
| Dashboards | Dashboard Builder Agent | Suggests dashboard layouts and related widgets |
| Reports | Report Writer Agent | Drafts report sections and export placeholders |
| Knowledge | RAG Knowledge Agent | Searches workspace PDFs, SOPs, policies, contracts, and meeting notes, with pgvector-ready upgrade path |
| Memory | Memory Agent | Stores recent AI memory in MongoDB |
| Recommendations | Recommendation Agent | Suggests dashboards, reports, follow-ups, KPIs, and opportunities |
| Compliance | Security & Compliance Agent | Checks RBAC, workspace isolation, query permissions, PII, and credential protection |
| Governance | Cost Governance Agent | Tracks token usage, estimates AI/query cost, enforces usage status, and warns on expensive workflows |
| Explanation | Explanation Agent | Explains generated queries and AI reasoning in business language |

## LangGraph Behavior

- Uses `StateGraph` with shared `InsightAIState`.
- Runs Data Quality Agent immediately after Schema Intelligence Agent.
- Runs Data Ingestion / ETL Agent only for import/upload/sync intents.
- Routes ambiguous prompts directly to compliance and explanation without query generation.
- Routes MongoDB requests to the MongoDB Query Agent and SQL requests to the SQL Generation Agent.
- Runs Anomaly Detection Agent before Root Cause Analysis and routes to RCA when anomaly severity requires it.
- Routes root-cause questions through Root Cause Analysis before forecasting and visualization.
- Runs Cost Governance Agent before the final Explanation Agent.
- Keeps deterministic behavior when `OPENAI_API_KEY` is missing.
- Records every agent invocation with latency, token estimates, success/error state, and retry count.
- Persists workflow traces and intermediate state in MongoDB collection `agent_traces`.
- Persists new production outputs in `agent_traces.agent_outputs`.
- Stores user/workspace AI memory in MongoDB collection `ai_memory`.

## Monitoring

Added Admin endpoints:

- `GET /api/v1/admin/agents`
- `GET /api/v1/admin/agents/traces`

The Admin Panel now shows:

- Registered agents and responsibilities
- Recent workflow traces
- Execution order
- Agent invocation count
- Retry count
- Token totals
- Error summaries
- Final confidence score
- Data quality score
- Anomaly severity
- ETL status
- Query cost score

## Bugs Found and Fixed

- Clarification-only workflows kept a generic provider name and broke existing usage-log expectations. Fixed by normalizing provider mode to `mock` or `openai-configured`.
- Clarification text drifted away from the tested UI copy. Fixed with explicit `Please clarify the metric...` wording.
- Clarification responses showed `Query validated and executed.` in the frontend. Fixed to display `Clarification required.`.
- Workflow finalization persisted before and after result execution. Fixed trace persistence to update the same trace instead of inserting duplicates.

## Validation

| Command | Result |
| --- | --- |
| `python -m pytest` | Passed: 21 tests |
| `npm.cmd audit --audit-level=moderate` | Passed: found 0 vulnerabilities |
| `npm.cmd run test` | Passed |
| `npm.cmd run build` | Passed |
| `npm.cmd run test:e2e` | Passed: 2 tests |

## Remaining Limitations

- The RAG Knowledge Agent now performs deterministic workspace document search; live vector indexing with pgvector remains a staging follow-up.
- Token usage is estimated in deterministic/mock mode because no live LLM usage payload exists without OpenAI execution.
- Independent-agent parallel execution is represented through graph branching-ready node boundaries, but the current workflow favors deterministic sequential execution for stable local tests.
- Next remains on `16.3.0-canary.69` to keep the PostCSS audit clean.

## Production Readiness

Updated score: 9/10

The multi-agent architecture is now extensible and observable. The last production point is reserved for staging validation against managed Redis, MongoDB, OpenAI, and a real pgvector knowledge base.
