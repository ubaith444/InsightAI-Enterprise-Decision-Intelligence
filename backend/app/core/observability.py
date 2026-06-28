import time
from collections import defaultdict
from typing import Any

REQUEST_METRICS: dict[str, Any] = {
    "requests_total": 0,
    "errors_total": 0,
    "latency_ms_total": 0.0,
    "paths": defaultdict(int),
}


def record_request(path: str, status_code: int, latency_ms: float) -> None:
    REQUEST_METRICS["requests_total"] += 1
    REQUEST_METRICS["latency_ms_total"] += latency_ms
    REQUEST_METRICS["paths"][path] += 1
    if status_code >= 500:
        REQUEST_METRICS["errors_total"] += 1


def metrics_snapshot() -> dict[str, Any]:
    total = max(int(REQUEST_METRICS["requests_total"]), 1)
    return {
        "requests_total": REQUEST_METRICS["requests_total"],
        "errors_total": REQUEST_METRICS["errors_total"],
        "average_latency_ms": round(float(REQUEST_METRICS["latency_ms_total"]) / total, 2),
        "paths": dict(REQUEST_METRICS["paths"]),
        "timestamp": time.time(),
    }


def prometheus_metrics() -> str:
    snapshot = metrics_snapshot()
    return "\n".join(
        [
            f"insightai_requests_total {snapshot['requests_total']}",
            f"insightai_errors_total {snapshot['errors_total']}",
            f"insightai_average_latency_ms {snapshot['average_latency_ms']}",
        ]
    )
