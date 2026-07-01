import asyncio
import logging
import sys

from app.core.database import async_session_factory
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.models.verification_code import VerificationCode  # noqa: F401 — needed to register the relationship target
from app.repositories.user_repository import UserRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_admin(email: str, password: str) -> None:
    async with async_session_factory() as db:
        repo = UserRepository(db)
        existing_user = await repo.get_by_email(email)

        if existing_user is not None:
            existing_user.role = UserRole.ADMIN
            existing_user.is_verified = True
            await db.commit()
            logger.info("Existing user '%s' promoted to admin.", email)
            return

        admin = User(
            email=email,
            hashed_password=hash_password(password),
            role=UserRole.ADMIN,
            is_verified=True,
        )
        db.add(admin)
        await db.commit()
        logger.info("Admin user '%s' created.", email)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python -m app.scripts.create_admin <email> <password>")
        sys.exit(1)

    asyncio.run(create_admin(sys.argv[1], sys.argv[2]))