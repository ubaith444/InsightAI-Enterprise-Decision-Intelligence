from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import User
from app.schemas.common import AIQuestion, QueryResult, QueryValidationRequest
from app.security.query_safety import validate_query
from app.models.entities import Role
from app.security.rate_limit import check_rate_limit, sanitize_text
from app.security.rbac import ensure_connection_access, ensure_workspace_access, require_role
from app.services.connectors import get_connection_or_404
from app.services.query_execution import ask_ai

router = APIRouter(prefix="/ai", tags=["AI Data Chat"])


@router.post("/ask", response_model=QueryResult)
def ask(payload: AIQuestion, user: User = Depends(require_role(Role.analyst)), db: Session = Depends(get_db)) -> dict:
    ensure_workspace_access(db, user, payload.workspace_id)
    check_rate_limit(f"ai:{payload.workspace_id}:{user.id}", limit=120, window_seconds=60)
    payload.question = sanitize_text(payload.question)
    connection = get_connection_or_404(db, payload.connection_id)
    ensure_connection_access(db, user, connection)
    return ask_ai(db, user, payload.workspace_id, payload.question, connection, payload.engine, payload.execute)


@router.post("/validate")
def validate(payload: QueryValidationRequest) -> dict:
    safe, query, error = validate_query(payload.engine, payload.query)
    return {"safe": safe, "query": query, "error": error}
