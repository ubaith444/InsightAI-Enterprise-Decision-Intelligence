# InsightAI System Architecture

InsightAI is a multi-tenant business intelligence copilot composed of a
Next.js frontend, FastAPI backend, LangGraph agent workflow, relational
analytics state, document-oriented workspace state, and asynchronous workers.

## Runtime components

| Component | Responsibility |
| --- | --- |
| Frontend | Authenticated SaaS UI, dashboards, chat, reports, lineage, settings, and admin screens. |
| FastAPI API | Auth, RBAC, workspace isolation, query safety, orchestration, audit logging, and REST/WebSocket endpoints. |
| LangGraph workflow | Multi-agent reasoning pipeline for classification, schema context, query generation, validation, insights, reports, governance, and monitoring. |
| PostgreSQL | Users, workspaces, memberships, database connections, query logs, AI usage logs, audit logs, and seeded business data. |
| MongoDB | Dashboards, reports, workspace resources, comments, approvals, notifications, knowledge documents, agent traces, and preferences. |
| Redis/Celery | Long-running jobs, report generation, imports, scheduled tasks, and async workflow execution. |
| OpenAI API | Optional model provider. The app falls back to deterministic local agents when `OPENAI_API_KEY` is not configured. |

## Request flow

1. The user authenticates with `POST /api/v1/auth/login` and receives a bearer
   token.
2. Frontend requests include the bearer token and workspace context.
3. FastAPI checks JWT validity, role rank, workspace membership, and connection
   ownership.
4. AI requests call the LangGraph workflow to classify intent, inspect schema,
   generate a query, validate safety, create insights, and record a trace.
5. Query execution enforces read-only SQL or MongoDB aggregation rules before
   returning rows, chart metadata, explanations, and recommendations.
6. Audits, usage, query logs, and agent traces are persisted for observability.

## Multi-tenancy

Every workspace-scoped resource includes a `workspace_id`. Super Admin users can
inspect all workspaces, while Admin, Analyst, and Viewer users require
membership in the target workspace. Database connections are checked through the
same workspace boundary before schema inspection or query execution.

## Diagrams

- System architecture: `diagrams/system-architecture.mmd`
- Deployment topology: `diagrams/deployment.mmd`
- Data lineage: `diagrams/data-lineage.mmd`
- LangGraph workflow: `diagrams/langgraph-workflow.mmd`
