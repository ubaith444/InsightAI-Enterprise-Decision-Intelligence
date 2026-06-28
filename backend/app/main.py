from contextlib import asynccontextmanager
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import admin, ai, audit, auth, connections, dashboards, enterprise, health, observability, queries, realtime, reports, resources, schema, users, workspaces
from app.core.config import get_settings
from app.core.observability import record_request
from app.db.seed import seed_application
from app.db.session import Base, SessionLocal, engine
from app.models import entities  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_application(db)
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="InsightAI API",
        version="1.0.0",
        description="AI-Powered Business Intelligence Copilot",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def metrics_middleware(request, call_next):
        started = time.perf_counter()
        response = await call_next(request)
        record_request(request.url.path, response.status_code, round((time.perf_counter() - started) * 1000, 2))
        return response

    app.include_router(health.router)
    for router in [
        auth.router,
        users.router,
        workspaces.router,
        connections.router,
        schema.router,
        ai.router,
        queries.router,
        dashboards.router,
        reports.router,
        resources.router,
        enterprise.router,
        realtime.router,
        observability.router,
        audit.router,
        admin.router,
    ]:
        app.include_router(router, prefix=settings.api_prefix)

    return app


app = create_app()
