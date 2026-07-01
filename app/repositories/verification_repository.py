import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.verification_code import VerificationCode


class VerificationRepository:
    """Encapsulates all database access for the VerificationCode model."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    def create(self, user_id: uuid.UUID, code: str, expires_at: datetime) -> VerificationCode:
        verification_code = VerificationCode(user_id=user_id, code=code, expires_at=expires_at)
        self.db.add(verification_code)
        return verification_code

    async def get_active_code(self, user_id: uuid.UUID, code: str) -> VerificationCode | None:
        """Return the most recent, unused verification code matching the given value."""
        result = await self.db.execute(
            select(VerificationCode)
            .where(
                VerificationCode.user_id == user_id,
                VerificationCode.code == code,
                VerificationCode.is_used.is_(False),
            )
            .order_by(VerificationCode.created_at.desc())
        )
        return result.scalars().first()