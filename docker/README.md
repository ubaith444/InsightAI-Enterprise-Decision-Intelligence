# Docker

InsightAI keeps service Dockerfiles close to each application:

- `backend/Dockerfile`
- `frontend/Dockerfile`
- `docker-compose.yml`

## Local stack

```powershell
copy .env.example .env
docker compose up --build
```

## Build checks

```powershell
docker compose build
```

## Release notes

- The backend image installs `backend/requirements.txt` and starts Uvicorn on
  port `8000`.
- The frontend image runs a production Next.js build and serves on port `3000`.
- Compose starts PostgreSQL, MongoDB, Redis, API, worker, and frontend services.
- Volumes `pgdata` and `mongodata` are local runtime state and must not be
  committed.
