from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import DatabaseConnection, Role, User, WorkspaceMember
from app.security.tokens import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)

ROLE_RANK = {
    Role.viewer: 1,
    Role.analyst: 2,
    Role.admin: 3,
    Role.super_admin: 4,
}


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    try:
        payload = decode_access_token(credentials.credentials)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from None
    user = db.get(User, payload["sub"])
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive or missing user")
    return user


def require_role(*roles: Role) -> Callable[[User], User]:
    minimum = max(ROLE_RANK[role] for role in roles)

    def dependency(user: User = Depends(get_current_user)) -> User:
        if ROLE_RANK[user.role] < minimum:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return user

    return dependency


def has_workspace_access(db: Session, user: User, workspace_id: str) -> bool:
    if user.role == Role.super_admin:
        return True
    return (
        db.query(WorkspaceMember)
        .filter(WorkspaceMember.workspace_id == workspace_id, WorkspaceMember.user_id == user.id)
        .first()
        is not None
    )


def ensure_workspace_access(db: Session, user: User, workspace_id: str) -> None:
    if not has_workspace_access(db, user, workspace_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Workspace access denied")


def ensure_connection_access(db: Session, user: User, connection: DatabaseConnection | None) -> None:
    if connection is not None:
        ensure_workspace_access(db, user, connection.workspace_id)
