# Contributing to InsightAI

Thank you for helping improve InsightAI. This project is prepared for a
professional public release, so contributions should keep the product secure,
documented, and easy to verify.

## Development workflow

1. Create a focused branch from `main`.
2. Copy `.env.example` to `.env` and use local-only secrets.
3. Install backend and frontend dependencies.
4. Add or update tests for behavior changes.
5. Run the validation commands before opening a pull request.

Backend:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m pytest
```

Frontend:

```powershell
cd frontend
npm.cmd ci
npm.cmd run lint
npm.cmd run build
npm.cmd run test:e2e
```

Full stack:

```powershell
docker compose up --build
```

## Pull request checklist

- No secrets, local databases, logs, caches, screenshots from private customer
  data, or generated dependency folders are committed.
- Public API changes are reflected in `docs/API.md`.
- Architecture or workflow changes are reflected in `docs/ARCHITECTURE.md`,
  `docs/LANGGRAPH_WORKFLOW.md`, and `diagrams/`.
- RBAC or authorization changes are reflected in `docs/RBAC_MATRIX.md`.
- Database model changes include migrations or clear migration notes.
- CI passes for backend tests, frontend type checks, builds, audits, and Docker
  image builds.

## Coding standards

- Keep user data workspace-scoped.
- Preserve read-only query safety guarantees.
- Prefer typed request/response schemas and small service functions.
- Keep UI changes accessible, responsive, and aligned with the existing app
  shell.
- Avoid broad refactors unless they are necessary for the change.

## Security

Report security issues privately through the repository security advisory flow
or to the maintainers before opening a public issue.
