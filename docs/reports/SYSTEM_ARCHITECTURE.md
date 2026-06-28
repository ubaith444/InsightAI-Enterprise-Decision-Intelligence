# InsightAI System Architecture

Date: 2026-06-27

## Summary

InsightAI V3 is structured as an Enterprise Multi-Agent Decision Intelligence Platform. The system combines a Next.js application, FastAPI API gateway, JWT/RBAC security, LangGraph multi-agent orchestration, workspace-scoped operational data, semantic metrics, RAG knowledge search, realtime analytics, ETL, observability, and deployment-ready container infrastructure.

## Runtime Architecture

```text
Next.js Frontend
  -> FastAPI API Gateway
  -> JWT Authentication + RBAC
  -> LangGraph Multi-Agent Supervisor
  -> AI Agent Layer
  -> Semantic Layer + Knowledge Layer
  -> Query Safety + Analytics Execution
  -> Dashboard, Report, Collaboration, Realtime APIs
  -> PostgreSQL + MongoDB + Redis/Celery
  -> External Databases, REST APIs, SaaS Connectors
```

## Major Subsystems

- Frontend: app-router pages for AI chat, dashboards, reports, integrations, semantic layer, lineage, collaboration, realtime, admin, billing, API keys, team, and settings.
- API Gateway: FastAPI route groups under `/api/v1`.
- Relational store: PostgreSQL-compatible SQLAlchemy models for users, workspaces, connections, audit logs, query logs, and AI usage.
- Document store: MongoDB-backed storage with local fallback for dashboards, reports, knowledge, settings, traces, semantic metrics, comments, approvals, lineage, ETL runs, and sync history.
- Queue layer: Redis/Celery for production async query execution and job expansion.
- AI layer: LangGraph Supervisor plus 34 specialized production agents, for 35 registered agents total.
- Realtime layer: snapshot API, WebSocket stream, and Server-Sent Events stream.
- Observability: request metrics, Prometheus text endpoint, agent traces, token usage, latency, retries, confidence, and workflow history.

## Multi-Tenant Boundary

Every operational resource is scoped by `workspace_id`. Backend APIs call workspace access checks before returning connections, schema, dashboards, reports, resources, lineage, realtime metrics, or audit-adjacent data.

## Deployment

The repository includes Docker Compose, app Dockerfiles, Kubernetes manifests, Nginx reverse proxy config, and a Terraform-ready folder for cloud infrastructure modules.
