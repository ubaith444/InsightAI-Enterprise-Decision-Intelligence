from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.common import Token, UserCreate, UserLogin
from app.services.auth import login_user, register_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=Token)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> Token:
    token, user = register_user(db, payload)
    return Token(access_token=token, user=user)


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)) -> Token:
    token, user = login_user(db, payload)
    return Token(access_token=token, user=user)


@router.get("/google-placeholder")
def google_placeholder() -> dict:
    return {"status": "placeholder", "message": "Google OAuth is reserved for production identity provider setup."}
