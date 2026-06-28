from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Role, User
from app.security.rbac import ensure_workspace_access, get_current_user, require_role
from app.services.enterprise_integrations import connector_catalog, import_dataset, list_etl_runs, list_sync_history, sync_rest_api, test_rest_api

router = APIRouter(prefix="/enterprise", tags=["Enterprise Integrations"])


@router.get("/connectors/catalog")
def catalog(_: User = Depends(get_current_user)) -> dict:
    return connector_catalog()


@router.post("/api/test")
def test_api(payload: dict, user: User = Depends(require_role(Role.analyst)), db: Session = Depends(get_db)) -> dict:
    ensure_workspace_access(db, user, payload["workspace_id"])
    return test_rest_api(payload["url"], payload.get("auth_header"))


@router.post("/api/sync")
def sync_api(payload: dict, user: User = Depends(require_role(Role.analyst)), db: Session = Depends(get_db)) -> dict:
    ensure_workspace_access(db, user, payload["workspace_id"])
    return sync_rest_api(payload["workspace_id"], payload["url"], payload.get("auth_header"), payload.get("cursor"), payload.get("provider"))


@router.get("/api/sync-history")
def sync_history(workspace_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict]:
    ensure_workspace_access(db, user, workspace_id)
    return list_sync_history(workspace_id)


@router.post("/etl/import")
async def etl_import(
    workspace_id: str = Form(...),
    source_type: str = Form("csv"),
    file: UploadFile = File(...),
    user: User = Depends(require_role(Role.analyst)),
    db: Session = Depends(get_db),
) -> dict:
    ensure_workspace_access(db, user, workspace_id)
    return import_dataset(workspace_id, file.filename or "upload", await file.read(), source_type)


@router.get("/etl/runs")
def etl_runs(workspace_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict]:
    ensure_workspace_access(db, user, workspace_id)
    return list_etl_runs(workspace_id)
