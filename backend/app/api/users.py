from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import User
from app.schemas.common import UserRead
from app.security.rbac import get_current_user, require_role
from app.models.entities import Role

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserRead)
def me(user: User = Depends(get_current_user)) -> User:
    return user


@router.get("", response_model=list[UserRead])
def list_users(_: User = Depends(require_role(Role.admin)), db: Session = Depends(get_db)) -> list[User]:
    return db.query(User).order_by(User.created_at.desc()).all()
