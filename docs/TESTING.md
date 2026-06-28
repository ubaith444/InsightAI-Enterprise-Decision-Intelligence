# Testing Guide

InsightAI includes backend unit/API tests, frontend type checks, frontend build
verification, Playwright E2E flows, Docker build checks, and release smoke
checks.

## Backend

```powershell
cd backend
python -m pytest
```

Coverage focus:

- Auth and workspace flows
- Query safety
- AI journey and deterministic fallback
- Enterprise connector/import routes
- Production gap regression tests

## Frontend

```powershell
cd frontend
npm.cmd ci
npm.cmd run lint
npm.cmd run build
npm.cmd run test:e2e
```

`npm run lint` and `npm run test` currently run TypeScript checks. Playwright
tests live in `frontend/e2e/` and demo capture specs live in `frontend/demo/`.

## Docker

```powershell
docker compose build
docker compose up
```

Smoke checks:

- `GET http://127.0.0.1:8000/health`
- `GET http://127.0.0.1:8000/docs`
- Open `http://127.0.0.1:3000`
- Login with the seeded demo account documented in `README.md`

## CI

GitHub Actions runs backend tests, frontend install/typecheck/build/audit/E2E,
and Docker image builds. See `.github/workflows/ci.yml`.
