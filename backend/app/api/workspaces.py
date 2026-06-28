from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import User, Workspace
from app.schemas.common import WorkspaceCreate, WorkspaceRead
from app.security.rbac import get_current_user
from app.services.workspaces import create_workspace

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])


@router.get("", response_model=list[WorkspaceRead])
def list_workspaces(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[Workspace]:
    if user.role.value == "Super Admin":
        return db.query(Workspace).order_by(Workspace.created_at.desc()).all()
    return [membership.workspace for membership in user.memberships]


@router.post("", response_model=WorkspaceRead)
def create(payload: WorkspaceCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Workspace:
    return create_workspace(db, user, payload)
