from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import AuditLog, Role, User
from app.schemas.common import AuditRead
from app.security.rbac import ensure_workspace_access, require_role

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


@router.get("", response_model=list[AuditRead])
def list_logs(workspace_id: str | None = None, user: User = Depends(require_role(Role.admin)), db: Session = Depends(get_db)) -> list[AuditLog]:
    query = db.query(AuditLog)
    if workspace_id:
        ensure_workspace_access(db, user, workspace_id)
        query = query.filter(AuditLog.workspace_id == workspace_id)
    return query.order_by(AuditLog.created_at.desc()).limit(100).all()
