from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import AuditAction, User
from app.schemas.common import DashboardCreate
from app.security.rbac import ensure_workspace_access, get_current_user
from app.services.audit import audit
from app.services.documents import create_dashboard, delete_dashboard, duplicate_dashboard, export_document, get_dashboard, list_dashboards, update_dashboard

router = APIRouter(prefix="/dashboards", tags=["Dashboards"])


@router.get("")
def list_items(workspace_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict]:
    ensure_workspace_access(db, user, workspace_id)
    return list_dashboards(workspace_id)


@router.post("")
def create(payload: DashboardCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    ensure_workspace_access(db, user, payload.workspace_id)
    dashboard = create_dashboard(payload.model_dump())
    audit(db, AuditAction.dashboard_created, "dashboard", user.id, payload.workspace_id, dashboard["id"])
    dashboard["created_by"] = user.id
    return dashboard


@router.put("/{dashboard_id}")
def update(dashboard_id: str, payload: DashboardCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    ensure_workspace_access(db, user, payload.workspace_id)
    dashboard = update_dashboard(dashboard_id, payload.model_dump())
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return dashboard


@router.delete("/{dashboard_id}")
def delete(dashboard_id: str, workspace_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    ensure_workspace_access(db, user, workspace_id)
    return {"deleted": delete_dashboard(dashboard_id)}


@router.post("/{dashboard_id}/duplicate")
def duplicate(dashboard_id: str, workspace_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    ensure_workspace_access(db, user, workspace_id)
    dashboard = duplicate_dashboard(dashboard_id)
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return dashboard


@router.get("/{dashboard_id}/export")
def export(dashboard_id: str, workspace_id: str, format: str = "csv", user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Response:
    ensure_workspace_access(db, user, workspace_id)
    content, media_type, filename = export_document(get_dashboard(dashboard_id), format)
    return Response(content=content, media_type=media_type, headers={"Content-Disposition": f'attachment; filename="{filename}"'})
