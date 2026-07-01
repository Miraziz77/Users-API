from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    """Schema for the user registration request."""

    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str | None = None
    last_name: str | None = None


class LoginRequest(BaseModel):
    """Schema for the login request."""

    email: EmailStr
    password: str


class VerifyRequest(BaseModel):
    """Schema for confirming an email verification code."""

    email: EmailStr
    code: str


class RefreshRequest(BaseModel):
    """Schema for refreshing an access token using a refresh token."""

    refresh_token: str