# Deployment Guide

This guide covers local production-like Docker Compose, container images, and
production deployment assets.

## Local Docker Compose

```powershell
copy .env.example .env
docker compose up --build
```

Services:

- Frontend: `http://127.0.0.1:3000`
- API docs: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/health`
- PostgreSQL: `127.0.0.1:5432`
- MongoDB: `127.0.0.1:27017`
- Redis: `127.0.0.1:6379`

## Production settings

Set these values outside source control:

- `APP_ENV=production`
- `SECRET_KEY`
- `DATABASE_URL`
- `MONGO_URL`
- `MONGO_DATABASE`
- `REDIS_URL`
- `OPENAI_API_KEY`
- `NEXT_PUBLIC_API_URL`

Use managed PostgreSQL, MongoDB, and Redis for production. Rotate the
`SECRET_KEY` with a planned token invalidation window.

## Containers

- Backend image: `backend/Dockerfile`
- Frontend image: `frontend/Dockerfile`
- Compose stack: `docker-compose.yml`
- Docker notes: `docker/README.md`

## Kubernetes and edge

Deployment examples are in:

- `deploy/kubernetes/`
- `deploy/nginx/insightai.conf`
- `deploy/terraform/README.md`

Before a production launch, configure TLS, domain routing, origin allowlists,
container resource limits, backup policies, log retention, and external secret
management.
