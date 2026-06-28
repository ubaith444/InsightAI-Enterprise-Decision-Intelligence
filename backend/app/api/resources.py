from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Role, User
from app.schemas.common import ExportRequest, KnowledgeDocumentCreate, KnowledgeSearchRequest, NotificationCreate, ScheduledReportCreate, WorkspaceResourceCreate
from app.schemas.common import ActivityCreate, ApprovalCreate, CommentCreate, SemanticMetricCreate
from app.security.rbac import ensure_workspace_access, get_current_user, require_role
from app.services.workspace_resources import (
    create_export,
    create_knowledge_document,
    create_notification,
    create_resource,
    create_scheduled_report,
    create_semantic_metric,
    data_lineage,
    delete_resource,
    create_comment,
    list_resource,
    list_comments,
    record_activity,
    request_approval,
    search_knowledge,
    semantic_layer,
    source_health,
    update_resource,
    usage_analytics,
)

router = APIRouter(prefix="/resources", tags=["Workspace Resources"])

COLLECTIONS = {
    "business-glossary": "business_glossary",
    "saved-prompts": "saved_prompts",
    "api-keys": "api_keys",
    "billing": "billing",
    "team": "team_management",
    "workspace-settings": "workspace_settings",
    "profile-settings": "profile_settings",
    "knowledge-documents": "knowledge_documents",
    "semantic-metrics": "semantic_metrics",
    "comments": "comments",
    "activity-feed": "activity_feed",
    "approvals": "approvals",
}


@router.get("/semantic-layer")
def semantic(workspace_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    ensure_workspace_access(db, user, workspace_id)
    return semantic_layer(workspace_id)


@router.post("/semantic-metrics")
def semantic_metric(payload: SemanticMetricCreate, user: User = Depends(require_role(Role.admin)), db: Session = Depends(get_db)) -> dict:
    ensure_workspace_access(db, user, payload.workspace_id)
    return create_semantic_metric(payload.workspace_id, payload.name, payload.definition, payload.formula, payload.owner, payload.dimensions, payload.tags)


@router.get("/data-lineage")
def lineage(workspace_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    ensure_workspace_access(db, user, workspace_id)
    return data_lineage(db, workspace_id)


@router.get("/comments/list")
def comments(workspace_id: str, target_type: str | None = None, target_id: str | None = None, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict]:
    ensure_workspace_access(db, user, workspace_id)
    return list_comments(workspace_id, target_type, target_id)


@router.post("/comments")
def comment(payload: CommentCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    ensure_workspace_access(db, user, payload.workspace_id)
    return create_comment(payload.workspace_id, payload.target_type, payload.target_id, user.id, payload.body, payload.mentions)


@router.get("/activity-feed")
def activity_feed(workspace_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict]:
    ensure_workspace_access(db, user, workspace_id)
    return list_resource("activity_feed", workspace_id)


@router.post("/activity")
def activity(payload: ActivityCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    ensure_workspace_access(db, user, payload.workspace_id)
    return record_activity(payload.workspace_id, user.id, payload.action, payload.entity_type, payload.entity_id, payload.payload)


@router.get("/approvals/list")
def approvals(workspace_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict]:
    ensure_workspace_access(db, user, workspace_id)
    return list_resource("approvals", workspace_id)


@router.post("/approvals")
def approval(payload: ApprovalCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    ensure_workspace_access(db, user, payload.workspace_id)
    return request_approval(payload.workspace_id, user.id, payload.target_type, payload.target_id, payload.action, payload.requested_reason)


@router.get("/notifications/list")
def notifications(workspace_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict]:
    ensure_workspace_access(db, user, workspace_id)
    return list_resource("notifications", workspace_id)


@router.post("/notifications")
def notify(payload: NotificationCreate, user: User = Depends(require_role(Role.analyst)), db: Session = Depends(get_db)) -> dict:
    ensure_workspace_access(db, user, payload.workspace_id)
    return create_notification(payload.workspace_id, payload.title, payload.message, payload.level, payload.payload)


@router.get("/scheduled-reports/list")
def scheduled_reports(workspace_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict]:
    ensure_workspace_access(db, user, workspace_id)
    return list_resource("scheduled_reports", workspace_id)


@router.post("/scheduled-reports")
def schedule_report(payload: ScheduledReportCreate, user: User = Depends(require_role(Role.analyst)), db: Session = Depends(get_db)) -> dict:
    ensure_workspace_access(db, user, payload.workspace_id)
    return create_scheduled_report(payload.workspace_id, payload.name, payload.cadence, payload.report_type, payload.delivery_channels, payload.payload)


@router.post("/exports")
def export(payload: ExportRequest, user: User = Depends(require_role(Role.analyst)), db: Session = Depends(get_db)) -> dict:
    ensure_workspace_access(db, user, payload.workspace_id)
    return create_export(payload.workspace_id, payload.format, payload.source_type, payload.source_id, payload.rows)


@router.get("/exports/list")
def exports(workspace_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict]:
    ensure_workspace_access(db, user, workspace_id)
    return list_resource("exports", workspace_id)


@router.get("/source-health/list")
def health(workspace_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict]:
    ensure_workspace_access(db, user, workspace_id)
    return source_health(db, workspace_id)


@router.get("/usage/analytics")
def usage(workspace_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    ensure_workspace_access(db, user, workspace_id)
    return usage_analytics(db, workspace_id)


@router.post("/knowledge-documents")
def knowledge_document(payload: KnowledgeDocumentCreate, user: User = Depends(require_role(Role.analyst)), db: Session = Depends(get_db)) -> dict:
    ensure_workspace_access(db, user, payload.workspace_id)
    return create_knowledge_document(payload.workspace_id, payload.title, payload.document_type, payload.content, payload.source_uri, payload.tags)


@router.post("/knowledge-search")
def knowledge_search(payload: KnowledgeSearchRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    ensure_workspace_access(db, user, payload.workspace_id)
    return search_knowledge(payload.workspace_id, payload.query, payload.document_types, payload.limit)


@router.get("/{resource_type}")
def list_items(resource_type: str, workspace_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict]:
    ensure_workspace_access(db, user, workspace_id)
    collection = COLLECTIONS.get(resource_type)
    if not collection:
        return []
    return list_resource(collection, workspace_id)


@router.post("")
def create_item(payload: WorkspaceResourceCreate, user: User = Depends(require_role(Role.analyst)), db: Session = Depends(get_db)) -> dict:
    ensure_workspace_access(db, user, payload.workspace_id)
    collection = COLLECTIONS.get(payload.resource_type, payload.resource_type.replace("-", "_"))
    return create_resource(collection, payload.workspace_id, payload.name, payload.payload)


@router.put("/{resource_type}/{resource_id}")
def update_item(resource_type: str, resource_id: str, payload: WorkspaceResourceCreate, user: User = Depends(require_role(Role.analyst)), db: Session = Depends(get_db)) -> dict:
    ensure_workspace_access(db, user, payload.workspace_id)
    collection = COLLECTIONS.get(resource_type, resource_type.replace("-", "_"))
    updated = update_resource(collection, payload.workspace_id, resource_id, {"name": payload.name, "payload": payload.payload})
    return updated or {"error": "not_found"}


@router.delete("/{resource_type}/{resource_id}")
def delete_item(resource_type: str, resource_id: str, workspace_id: str, user: User = Depends(require_role(Role.admin)), db: Session = Depends(get_db)) -> dict:
    ensure_workspace_access(db, user, workspace_id)
    collection = COLLECTIONS.get(resource_type, resource_type.replace("-", "_"))
    return {"deleted": delete_resource(collection, workspace_id, resource_id)}
