"""
ClipEngine — Celery Configuration
"""

from celery import Celery
from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "clipengine",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,

    # Queue routing
    task_routes={
        "app.tasks.video_tasks.generate_video_task": {
            "queue": "default",  # overridden per-call with .apply_async(queue=...)
        },
    },

    # Define queues
    task_queues={
        "free": {"exchange": "free", "routing_key": "free"},
        "creator": {"exchange": "creator", "routing_key": "creator"},
        "priority": {"exchange": "priority", "routing_key": "priority"},
    },

    # Concurrency limits per queue (configured per worker at startup)
    worker_concurrency=3,

    # Task result expiry (24 hours)
    result_expires=86400,

    # Task time limits
    task_soft_time_limit=600,   # 10 minutes soft limit
    task_time_limit=900,        # 15 minutes hard limit
)

