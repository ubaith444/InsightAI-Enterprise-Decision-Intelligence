from sqlalchemy.orm import Session

from app.models import AuditAction, AuditLog


def audit(
    db: Session,
    action: AuditAction,
    entity_type: str,
    actor_id: str | None = None,
    workspace_id: str | None = None,
    entity_id: str | None = None,
    metadata: dict | None = None,
) -> AuditLog:
    item = AuditLog(
        workspace_id=workspace_id,
        actor_id=actor_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        metadata_json=metadata or {},
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
