import asyncio
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete

from app.core.celery_app import celery_app
from app.core.config import settings
from app.core.database import async_session_factory
from app.models.user import User

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.cleanup.delete_unverified_users")
def delete_unverified_users() -> dict:
    """Delete users who have not verified their email within the allowed TTL.

    Celery tasks are synchronous by nature, so we run the async DB logic
    inside asyncio.run(). With more time this could use a dedicated sync
    DB session instead to avoid the asyncio.run() overhead; however, reusing
    the existing async session factory keeps the codebase consistent and
    avoids duplicating database configuration.
    """
    return asyncio.run(_delete_unverified_users_async())


async def _delete_unverified_users_async() -> dict:
    """Async implementation of the cleanup logic."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=settings.UNVERIFIED_USER_TTL_DAYS)

    async with async_session_factory() as db:
        result = await db.execute(
            delete(User)
            .where(
                User.is_verified.is_(False),
                User.created_at < cutoff,
            )
            .returning(User.id)
        )
        await db.commit()
        deleted_ids = result.fetchall()

    count = len(deleted_ids)
    logger.info("Deleted %d unverified user(s) older than %d day(s).", count, settings.UNVERIFIED_USER_TTL_DAYS)
    return {"deleted_count": count}