from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import AuditAction, User
from app.schemas.common import ReportCreate
from app.security.rbac import ensure_workspace_access, get_current_user
from app.services.audit import audit
from app.services.documents import create_report, export_document, get_report, list_reports, update_report

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("")
def list_items(workspace_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict]:
    ensure_workspace_access(db, user, workspace_id)
    return list_reports(workspace_id)


@router.post("")
def create(payload: ReportCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    ensure_workspace_access(db, user, payload.workspace_id)
    report = create_report(payload.model_dump())
    audit(db, AuditAction.report_generated, "report", user.id, payload.workspace_id, report["id"])
    report["created_by"] = user.id
    return report


@router.put("/{report_id}")
def update(report_id: str, payload: ReportCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    ensure_workspace_access(db, user, payload.workspace_id)
    report = update_report(report_id, payload.model_dump())
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.get("/{report_id}/download")
def download(report_id: str, workspace_id: str, format: str = "pdf", user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Response:
    ensure_workspace_access(db, user, workspace_id)
    content, media_type, filename = export_document(get_report(report_id), format)
    return Response(content=content, media_type=media_type, headers={"Content-Disposition": f'attachment; filename="{filename}"'})
