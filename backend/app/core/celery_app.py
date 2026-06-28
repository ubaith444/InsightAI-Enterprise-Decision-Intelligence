from celery import Celery

from app.core.config import get_settings

settings = get_settings()
result_backend = "cache+memory://" if settings.celery_task_always_eager else settings.redis_url

celery_app = Celery("insightai", broker=settings.redis_url, backend=result_backend)
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    task_track_started=True,
    task_always_eager=settings.celery_task_always_eager,
    task_store_eager_result=True,
    result_expires=3600,
)

celery_app.autodiscover_tasks(["app.services"])
