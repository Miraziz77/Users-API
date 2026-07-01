import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserUpdate


class UserService:
    """Business logic for retrieving, listing, updating and deleting users."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.users = UserRepository(db)

    async def get_by_id(self, user_id: uuid.UUID) -> User:
        user = await self.users.get_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user

    async def list_users(self, offset: int = 0, limit: int = 100) -> list[User]:
        return await self.users.list_all(offset=offset, limit=limit)

    async def update_user(
        self, user_id: uuid.UUID, data: UserUpdate, current_user: User
    ) -> User:
        """Update a user's profile.

        A regular user may only update their own profile; an admin may
        update any user's profile.
        """
        if current_user.role != UserRole.ADMIN and current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own profile",
            )

        user = await self.get_by_id(user_id)

        update_fields = data.model_dump(exclude_unset=True)
        for field, value in update_fields.items():
            setattr(user, field, value)

        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete_user(self, user_id: uuid.UUID) -> None:
        user = await self.get_by_id(user_id)
        await self.users.delete(user)
        await self.db.commit()
