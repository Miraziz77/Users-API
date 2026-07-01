import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin, get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserRead, UserUpdate
from app.services.user_service import UserService

router = APIRouter(tags=["users 🙎‍♂️"])


@router.get(
    "/me",
    response_model=UserRead,
    summary="Get the current user",
    description="Returns the profile of the currently authenticated user.",
)
async def get_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.get(
    "/users",
    response_model=list[UserRead],
    summary="List all users",
    description="Returns a paginated list of all users. Admin access required.",
)
async def list_users(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> list[User]:
    return await UserService(db).list_users(offset=offset, limit=limit)


@router.get(
    "/users/{user_id}",
    response_model=UserRead,
    summary="Get a user by ID",
    description="Returns a single user by their ID. Admin access required.",
)
async def get_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> User:
    return await UserService(db).get_by_id(user_id)


@router.patch(
    "/users/{user_id}",
    response_model=UserRead,
    summary="Update a user",
    description="Partially updates a user's first and last name. Users can only update their own profile; admins can update any user.",
)
async def update_user(
    user_id: uuid.UUID,
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> User:
    return await UserService(db).update_user(user_id, data, current_user)


@router.delete(
    "/users/{user_id}",
    status_code=204,
    summary="Delete a user",
    description="Deletes a user by their ID. Admin access required.",
)
async def delete_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> None:
    await UserService(db).delete_user(user_id)