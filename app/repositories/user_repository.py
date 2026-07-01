import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    """Encapsulates all database access for the User model."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def list_all(self, offset: int = 0, limit: int = 100) -> list[User]:
        result = await self.db.execute(select(User).offset(offset).limit(limit))
        return list(result.scalars().all())

    def create(
        self,
        email: str,
        hashed_password: str,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> User:
        user = User(
            email=email,
            hashed_password=hashed_password,
            first_name=first_name,
            last_name=last_name,
        )
        self.db.add(user)
        return user

    async def delete(self, user: User) -> None:
        await self.db.delete(user)