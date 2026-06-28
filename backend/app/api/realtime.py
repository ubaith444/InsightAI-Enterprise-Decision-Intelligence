import asyncio
from datetime import datetime

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import QueryLog, User
from app.security.rbac import ensure_workspace_access, get_current_user
from app.services.workspace_resources import usage_analytics

router = APIRouter(prefix="/realtime", tags=["Realtime Analytics"])


@router.get("/snapshot")
def snapshot(workspace_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    ensure_workspace_access(db, user, workspace_id)
    recent = db.query(QueryLog).filter(QueryLog.workspace_id == workspace_id).order_by(QueryLog.created_at.desc()).limit(5).all()
    return {
        "workspace_id": workspace_id,
        "timestamp": datetime.utcnow(),
        "kpis": usage_analytics(db, workspace_id),
        "recent_queries": [{"question": item.question, "status": item.status, "row_count": item.row_count} for item in recent],
        "refresh_intervals": [5, 15, 30, 60],
    }


@router.get("/events")
async def server_sent_events(workspace_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> StreamingResponse:
    ensure_workspace_access(db, user, workspace_id)

    async def stream():
        for _ in range(3):
            yield f"event: live_metrics\ndata: {{\"workspace_id\":\"{workspace_id}\",\"timestamp\":\"{datetime.utcnow().isoformat()}\",\"active\":true}}\n\n"
            await asyncio.sleep(1)

    return StreamingResponse(stream(), media_type="text/event-stream")


@router.websocket("/ws/{workspace_id}")
async def websocket_endpoint(websocket: WebSocket, workspace_id: str) -> None:
    await websocket.accept()
    try:
        while True:
            await websocket.send_json(
                {
                    "workspace_id": workspace_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "event": "live_metrics",
                    "metrics": {"active": True, "refresh_intervals": [5, 15, 30, 60]},
                }
            )
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        return
