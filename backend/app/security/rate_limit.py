import time
from collections import defaultdict, deque

from fastapi import HTTPException, status

_calls: dict[str, deque[float]] = defaultdict(deque)


def check_rate_limit(key: str, limit: int = 60, window_seconds: int = 60) -> None:
    now = time.time()
    bucket = _calls[key]
    while bucket and now - bucket[0] > window_seconds:
        bucket.popleft()
    if len(bucket) >= limit:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded. Try again shortly.")
    bucket.append(now)


def sanitize_text(value: str, max_length: int = 2000) -> str:
    cleaned = " ".join(value.replace("\x00", "").split())
    return cleaned[:max_length]
