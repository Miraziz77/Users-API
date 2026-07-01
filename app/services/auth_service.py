import uuid
from datetime import datetime, timedelta, timezone

from fastapi import BackgroundTasks, HTTPException, status
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.email import send_verification_email_safe
from app.core.security import (
    TokenType,
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_verification_code,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.repositories.verification_repository import VerificationRepository
from app.schemas.auth import LoginRequest, SignupRequest, VerifyRequest
from app.schemas.token import AccessToken, TokenPair


class AuthService:
    """Business logic for registration, login, token refresh and verification."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.users = UserRepository(db)
        self.verifications = VerificationRepository(db)

    async def signup(self, data: SignupRequest, background_tasks: BackgroundTasks) -> User:
        if await self.users.get_by_email(data.email) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists",
            )

        user = self.users.create(
            email=data.email,
            hashed_password=hash_password(data.password),
            first_name=data.first_name,
            last_name=data.last_name,
        )
        await self.db.flush()

        code = generate_verification_code()
        self.verifications.create(
            user_id=user.id,
            code=code,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=settings.VERIFICATION_CODE_EXPIRE_HOURS),
        )
        await self.db.commit()
        await self.db.refresh(user)

        # Sent in the background so the client gets an immediate response
        # instead of waiting on the SMTP round-trip. Failures are only
        # logged (see send_verification_email_safe) since there is no
        # request/response cycle left to report them to.
        background_tasks.add_task(send_verification_email_safe, user.email, code)

        return user

    async def login(self, data: LoginRequest) -> TokenPair:
        user = await self.users.get_by_email(data.email)

        if user is None or not verify_password(data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        # Note: login is intentionally allowed for unverified users so they are
        # not locked out before completing verification. Access to protected
        # endpoints can still be restricted based on `is_verified` if needed.
        return TokenPair(
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id),
        )

    async def refresh(self, refresh_token: str) -> AccessToken:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

        try:
            payload = decode_token(refresh_token)
        except JWTError:
            raise credentials_exception

        if payload.get("type") != TokenType.REFRESH.value:
            raise credentials_exception

        try:
            user_id = uuid.UUID(payload.get("sub"))
        except (TypeError, ValueError):
            raise credentials_exception

        user = await self.users.get_by_id(user_id)
        if user is None:
            raise credentials_exception

        return AccessToken(access_token=create_access_token(user.id))

    async def verify(self, data: VerifyRequest) -> User:
        user = await self.users.get_by_email(data.email)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        if user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already verified",
            )

        verification_code = await self.verifications.get_active_code(user.id, data.code)
        if verification_code is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification code",
            )

        if verification_code.expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification code has expired",
            )

        verification_code.is_used = True
        user.is_verified = True
        await self.db.commit()
        await self.db.refresh(user)

        return user