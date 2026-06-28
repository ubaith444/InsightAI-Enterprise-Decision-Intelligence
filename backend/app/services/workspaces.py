import re

from sqlalchemy.orm import Session

from app.models import Role, User, Workspace, WorkspaceMember
from app.schemas.common import WorkspaceCreate


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def create_workspace(db: Session, user: User, payload: WorkspaceCreate) -> Workspace:
    base = slugify(payload.name)
    slug = base
    suffix = 2
    while db.query(Workspace).filter(Workspace.slug == slug).first():
        slug = f"{base}-{suffix}"
        suffix += 1
    workspace = Workspace(name=payload.name, slug=slug, owner_id=user.id)
    db.add(workspace)
    db.flush()
    db.add(WorkspaceMember(workspace_id=workspace.id, user_id=user.id, role=Role.admin))
    db.commit()
    db.refresh(workspace)
    return workspace
