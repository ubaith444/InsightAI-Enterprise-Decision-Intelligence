from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import User
from app.security.rbac import ensure_connection_access, get_current_user
from app.services.connectors import get_connection_or_404, read_schema

router = APIRouter(prefix="/schema", tags=["Schema Explorer"])


@router.get("")
def current_schema(connection_id: str | None = None, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    connection = get_connection_or_404(db, connection_id)
    ensure_connection_access(db, user, connection)
    return read_schema(connection)
