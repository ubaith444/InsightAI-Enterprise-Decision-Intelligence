# InsightAI v1.0.0 Release Notes

Initial public release of InsightAI, an AI-powered business intelligence
copilot for multi-tenant analytics teams.

## Included

- Next.js SaaS frontend with dashboards, AI data chat, reports, lineage,
  realtime analytics, settings, team/admin surfaces, and demo flows.
- FastAPI backend with JWT auth, RBAC, workspace isolation, audit logs, query
  logs, observability, and route groups for analytics workflows.
- LangGraph multi-agent workflow with deterministic fallback when
  `OPENAI_API_KEY` is not configured.
- PostgreSQL, MongoDB, Redis, and Celery Docker Compose stack.
- Demo business dataset, screenshots, demo video, architecture diagrams, and
  production-oriented documentation.
- CI for backend tests, frontend validation, audits, E2E, and Docker builds.

## Release checklist

1. Run `python -m pytest` in `backend/`.
2. Run `npm.cmd ci`, `npm.cmd run lint`, `npm.cmd run build`, and
   `npm.cmd run test:e2e` in `frontend/`.
3. Run `docker compose build`.
4. Confirm no `.env`, logs, local databases, caches, or dependency folders are
   staged.
5. Create the first release commit.
6. Tag the release:

```powershell
git tag -a v1.0.0 -m "InsightAI v1.0.0"
```
