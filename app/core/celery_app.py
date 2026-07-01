from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery(
    "users_api",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.cleanup"],
)

celery_app.conf.timezone = "UTC"

# Periodic task schedule: run the cleanup every hour.
# With more time this could be made configurable via environment variables.
celery_app.conf.beat_schedule = {
    "delete-unverified-users-every-hour": {
        "task": "app.tasks.cleanup.delete_unverified_users",
        "schedule": crontab(minute=0, hour="*"),
    },
}