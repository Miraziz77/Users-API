import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.user import UserRole


class UserRead(BaseModel):
    """Schema returned to clients when exposing user data."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    first_name: str | None
    last_name: str | None
    role: UserRole
    is_verified: bool
    created_at: datetime
    updated_at: datetime


class UserUpdate(BaseModel):
    """Schema for partial updates to a user (PATCH /users/{id}).

    All fields are optional since this is a partial update.
    Email and role changes are intentionally not allowed here to keep the
    scope limited to what the task requires; with more time this would be
    split into separate, more tightly permissioned endpoints
    (e.g. a dedicated role-change endpoint restricted to admins).
    """

    first_name: str | None = None
    last_name: str | None = None