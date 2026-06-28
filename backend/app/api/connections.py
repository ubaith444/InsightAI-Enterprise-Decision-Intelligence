from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import DatabaseConnection, Role, User
from app.schemas.common import ConnectionCreate, ConnectionRead
from app.security.rbac import ensure_connection_access, ensure_workspace_access, get_current_user, require_role
from app.services.connectors import create_connection, get_connection_or_404, read_schema, test_connection

router = APIRouter(prefix="/connections", tags=["Database Connections"])


@router.get("", response_model=list[ConnectionRead])
def list_connections(workspace_id: str | None = None, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[DatabaseConnection]:
    query = db.query(DatabaseConnection)
    if workspace_id:
        ensure_workspace_access(db, user, workspace_id)
        query = query.filter(DatabaseConnection.workspace_id == workspace_id)
    elif user.role != Role.super_admin:
        workspace_ids = [membership.workspace_id for membership in user.memberships]
        query = query.filter(DatabaseConnection.workspace_id.in_(workspace_ids))
    return query.order_by(DatabaseConnection.created_at.desc()).all()


@router.post("", response_model=ConnectionRead)
def create(payload: ConnectionCreate, user: User = Depends(require_role(Role.analyst)), db: Session = Depends(get_db)) -> DatabaseConnection:
    ensure_workspace_access(db, user, payload.workspace_id)
    return create_connection(db, user, payload)


@router.post("/{connection_id}/test")
def test(connection_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    connection = get_connection_or_404(db, connection_id)
    ensure_connection_access(db, user, connection)
    return test_connection(connection)


@router.get("/{connection_id}/schema")
def schema(connection_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    connection = get_connection_or_404(db, connection_id)
    ensure_connection_access(db, user, connection)
    return read_schema(connection)
