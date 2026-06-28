# Security Guide

InsightAI is designed for workspace-scoped analytics with read-only query
execution and auditable AI activity.

## Secrets

- Never commit `.env`, local databases, private keys, certificates, logs, or
  generated dependency folders.
- Use `.env.example` as the safe template.
- Rotate `SECRET_KEY` and connector credentials in production secret storage.
- `OPENAI_API_KEY` is optional and must be injected at runtime.

## Authentication and authorization

- JWT bearer tokens protect API routes.
- RBAC ranks are defined in `backend/app/security/rbac.py`.
- Workspace access is checked against `workspace_members`.
- Database connection access is derived from workspace ownership.

## Query safety

- SQL must be read-only `SELECT` or read-only CTE statements.
- Multiple statements and mutating keywords are blocked.
- MongoDB aggregation blocks mutating stages such as `$merge` and `$out`.
- Default limits and timeouts protect backend and database resources.

## Auditability

InsightAI records:

- Login events
- Connection creation
- Query generation and execution
- Dashboard/report creation
- AI usage
- Agent traces
- Admin analytics

## Responsible disclosure

Report suspected security issues privately through the repository security
advisory flow or directly to maintainers before public disclosure.
