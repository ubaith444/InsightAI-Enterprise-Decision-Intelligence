from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.ai.langgraph_workflow import list_agent_specs, list_agent_traces
from app.models import AIUsageLog, AuditLog, DatabaseConnection, QueryLog, Role, User, Workspace
from app.security.rbac import require_role

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/analytics")
def analytics(_: User = Depends(require_role(Role.admin)), db: Session = Depends(get_db)) -> dict:
    failed = db.query(QueryLog).filter(QueryLog.status == "failed").count()
    return {
        "users": db.query(User).count(),
        "workspaces": db.query(Workspace).count(),
        "connections": db.query(DatabaseConnection).count(),
        "query_logs": db.query(QueryLog).count(),
        "failed_queries": failed,
        "ai_usage_events": db.query(AIUsageLog).count(),
        "audit_events": db.query(AuditLog).count(),
        "rows_returned": db.query(func.coalesce(func.sum(QueryLog.row_count), 0)).scalar(),
        "system_health": {"api": "ok", "postgres": "configured", "mongodb": "fallback-ready", "redis": "configured"},
    }


@router.get("/agents")
def agents(_: User = Depends(require_role(Role.admin))) -> dict:
    return {"agents": list_agent_specs()}


@router.get("/agents/traces")
def agent_traces(workspace_id: str | None = None, _: User = Depends(require_role(Role.admin))) -> dict:
    traces = list_agent_traces(workspace_id)
    total_invocations = sum(len(trace.get("agent_trace", [])) for trace in traces)
    successful = sum(1 for trace in traces if trace.get("success"))
    return {
        "traces": traces,
        "summary": {
            "workflows": len(traces),
            "agent_invocations": total_invocations,
            "success_rate": round(successful / max(len(traces), 1), 2),
        },
    }
