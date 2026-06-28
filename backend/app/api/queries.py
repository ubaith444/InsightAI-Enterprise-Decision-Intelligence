from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import QueryLog, User
from app.schemas.common import QueryExecutionRequest
from app.security.query_safety import validate_query
from app.models.entities import Role
from app.security.rbac import ensure_connection_access, ensure_workspace_access, get_current_user, require_role
from app.services.jobs import enqueue_query_job, get_query_job
from app.services.connectors import get_connection_or_404
from app.services.query_execution import execute_mongo, execute_sql

router = APIRouter(prefix="/queries", tags=["Query Execution"])


@router.get("/history")
def history(workspace_id: str | None = None, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict]:
    query = db.query(QueryLog)
    if workspace_id:
        ensure_workspace_access(db, user, workspace_id)
        query = query.filter(QueryLog.workspace_id == workspace_id)
    elif user.role != Role.super_admin:
        workspace_ids = [membership.workspace_id for membership in user.memberships]
        query = query.filter(QueryLog.workspace_id.in_(workspace_ids))
    return [
        {
            "id": item.id,
            "question": item.question,
            "generated_query": item.generated_query,
            "engine": item.engine,
            "status": item.status,
            "row_count": item.row_count,
            "created_at": item.created_at,
        }
        for item in query.order_by(QueryLog.created_at.desc()).limit(50).all()
    ]


@router.post("/execute")
def execute(payload: QueryExecutionRequest, user: User = Depends(require_role(Role.analyst)), db: Session = Depends(get_db)) -> dict:
    ensure_workspace_access(db, user, payload.workspace_id)
    safe, query, error = validate_query(payload.engine, payload.query)
    if not safe:
        return {"safe": False, "error": error, "rows": []}
    connection = get_connection_or_404(db, payload.connection_id)
    ensure_connection_access(db, user, connection)
    if payload.async_job:
        return {"safe": True, "job": enqueue_query_job(payload.model_dump())}
    rows = execute_mongo(query) if payload.engine == "mongodb" else execute_sql(str(query), connection)
    return {"safe": True, "query": query, "rows": rows}


@router.get("/jobs/{job_id}")
def job_status(job_id: str, _: User = Depends(get_current_user)) -> dict:
    job = get_query_job(job_id)
    if not job:
        return {"status": "missing", "id": job_id}
    return job
