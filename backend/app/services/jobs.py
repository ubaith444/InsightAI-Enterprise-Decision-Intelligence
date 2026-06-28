from typing import Any

from celery.result import AsyncResult

from app.core.celery_app import celery_app
from app.db.session import SessionLocal
from app.services.connectors import get_connection_or_404
from app.services.query_execution import execute_mongo, execute_sql

_eager_results: dict[str, dict[str, Any]] = {}


@celery_app.task(name="insightai.execute_query")
def execute_query_task(payload: dict[str, Any]) -> dict[str, Any]:
    with SessionLocal() as db:
        connection = get_connection_or_404(db, payload.get("connection_id"))
        engine = payload["engine"]
        query = payload["query"]
        rows = execute_mongo(query, connection) if engine == "mongodb" else execute_sql(str(query), connection)
        return {"safe": True, "query": query, "rows": rows, "row_count": len(rows)}


def enqueue_query_job(payload: dict[str, Any]) -> dict[str, Any]:
    result = execute_query_task.delay(payload)
    if result.ready():
        _eager_results[result.id] = {
            "id": result.id,
            "status": result.status.lower(),
            "backend": "redis-celery",
            "result": result.result,
        }
    return {
        "id": result.id,
        "status": result.status.lower(),
        "backend": "redis-celery",
        "message": "Long-running query submitted to Celery using the configured Redis broker/backend.",
    }


def get_query_job(job_id: str) -> dict[str, Any]:
    if job_id in _eager_results:
        return _eager_results[job_id]
    result = AsyncResult(job_id, app=celery_app)
    response: dict[str, Any] = {"id": job_id, "status": result.status.lower(), "backend": "redis-celery"}
    if result.ready():
        response["result"] = result.result
    return response
