from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from app.core.observability import metrics_snapshot, prometheus_metrics

router = APIRouter(prefix="/observability", tags=["Observability"])


@router.get("/metrics")
def metrics() -> dict:
    return metrics_snapshot()


@router.get("/prometheus", response_class=PlainTextResponse)
def prometheus() -> str:
    return prometheus_metrics()
