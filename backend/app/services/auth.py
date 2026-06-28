import re

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import AuditAction, Role, User, Workspace, WorkspaceMember
from app.schemas.common import UserCreate, UserLogin
from app.security.passwords import hash_password, verify_password
from app.security.tokens import create_access_token
from app.services.audit import audit


def _slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def register_user(db: Session, payload: UserCreate) -> tuple[str, User]:
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    role = Role.super_admin if db.query(User).count() == 0 else Role.analyst
    user = User(email=payload.email, full_name=payload.full_name, hashed_password=hash_password(payload.password), role=role)
    db.add(user)
    db.flush()
    workspace = Workspace(name=f"{payload.full_name}'s Workspace", slug=_slugify(payload.full_name), owner_id=user.id)
    db.add(workspace)
    db.flush()
    db.add(WorkspaceMember(workspace_id=workspace.id, user_id=user.id, role=role))
    db.commit()
    db.refresh(user)
    token = create_access_token(user.id, {"role": user.role.value})
    return token, user


def login_user(db: Session, payload: UserLogin) -> tuple[str, User]:
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    audit(db, AuditAction.login, "user", actor_id=user.id, entity_id=user.id)
    return create_access_token(user.id, {"role": user.role.value}), user
