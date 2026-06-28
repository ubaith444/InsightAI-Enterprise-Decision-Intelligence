# InsightAI Deployment Guide

Date: 2026-06-27

## Prerequisites

- Docker and Docker Compose
- Node.js 22 for local frontend checks
- Python 3.11+ for local backend checks
- PostgreSQL, MongoDB, Redis for production-style deployment
- OpenAI API key for live AI generation

## Environment

Copy `.env.example` to `.env` and set production values.

Required production variables:

- `SECRET_KEY`
- `DATABASE_URL`
- `MONGO_URL`
- `REDIS_URL`
- `OPENAI_API_KEY`
- `CELERY_TASK_ALWAYS_EAGER=false`

Security note:

- Do not use the default `SECRET_KEY` in production.
- New database connection strings are encrypted with a key derived from `SECRET_KEY`; changing it later may make existing encrypted strings unreadable.

## Local Docker Run

```powershell
docker compose up --build
```

Services:

- Frontend: `http://127.0.0.1:3000`
- Backend: `http://127.0.0.1:8000`
- API docs: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/health`

## Seed Data

The app seeds on startup. You can also run:

```powershell
cd backend
python -m app.cli
```

Seed includes:

- Demo admin user
- Demo workspace
- Demo database connection
- Sales, Customers, Products, Orders, Employees, Regions, Expenses, Inventory
- Business glossary
- Saved prompts
- Demo dashboard
- Demo report

Demo login:

- Email: `admin@insightai.ai`
- Password: `InsightAI123`

## Migrations

Alembic is configured in `backend/alembic.ini`.

```powershell
cd backend
alembic upgrade head
```

The local demo also calls `Base.metadata.create_all` during app startup for fast smoke testing.

## Celery and Redis

Production-style async execution requires Redis and a worker:

```powershell
cd backend
celery -A app.core.celery_app.celery_app worker --loglevel=INFO
```

Use async jobs for:

- Long-running queries
- Report generation
- Dataset imports
- Scheduled report generation

## Health and Environment Validation

Check:

```powershell
curl http://127.0.0.1:8000/health
```

The response includes environment validation for secret key, database, MongoDB, Redis, and OpenAI mode.

## CI

GitHub Actions workflow:

- `.github/workflows/ci.yml`

CI runs:

- Backend pytest
- Frontend typecheck
- Frontend build
- npm audit
- Playwright E2E

## Kubernetes

Kubernetes-ready manifests live in `deploy/kubernetes`:

- `namespace.yaml`
- `configmap.yaml`
- `api-deployment.yaml`
- `web-deployment.yaml`
- `worker-deployment.yaml`
- `ingress.yaml`

Apply after building/publishing images and creating production secrets:

```powershell
kubectl apply -f deploy/kubernetes
```

## Nginx

Reverse proxy config:

- `deploy/nginx/insightai.conf`

The config forwards `/api`, `/health`, frontend traffic, and WebSocket upgrade traffic.

## Terraform-Ready Structure

Cloud infrastructure notes live in `deploy/terraform/README.md`. Add provider-specific modules for network, compute, managed data stores, secrets, object storage, and observability.

## Production Checklist

- Set strong `SECRET_KEY`
- Set `CELERY_TASK_ALWAYS_EAGER=false`
- Use managed PostgreSQL, MongoDB, and Redis
- Configure OpenAI key and usage limits
- Configure backup and restore policies
- Wire email, Slack, WhatsApp delivery providers
- Replace local PDF/PowerPoint byte generation with branded rendering services if required
- Add file storage for CSV/Excel imports
- Add pgvector ingestion for RAG knowledge
- Review RBAC assignments for workspace admins and viewers
