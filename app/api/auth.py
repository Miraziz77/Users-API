from fastapi import APIRouter, BackgroundTasks, Depends, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, RefreshRequest, SignupRequest, VerifyRequest
from app.schemas.token import AccessToken, TokenPair
from app.schemas.user import UserRead
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth 🛡️"])

# Local limiter instance for stricter per-endpoint rate limits on auth routes.
limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/signup",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Creates a new unverified user account and sends a verification code to the provided email.",
)
@limiter.limit("5/minute")
async def signup(
    request: Request,
    data: SignupRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> User:
    return await AuthService(db).signup(data, background_tasks)


@router.post(
    "/login",
    response_model=TokenPair,
    summary="Authenticate a user",
    description="Validates credentials and returns a new access/refresh token pair.",
)
@limiter.limit("10/minute")
async def login(
    request: Request,
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenPair:
    return await AuthService(db).login(data)


@router.post(
    "/refresh",
    response_model=AccessToken,
    summary="Refresh an access token",
    description="Issues a new access token from a valid, non-expired refresh token.",
)
@limiter.limit("20/minute")
async def refresh(
    request: Request,
    data: RefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> AccessToken:
    return await AuthService(db).refresh(data.refresh_token)


@router.post(
    "/verify",
    response_model=UserRead,
    summary="Verify a user's email",
    description="Confirms a verification code sent to the user's email and marks the account as verified.",
)
@limiter.limit("5/minute")
async def verify(
    request: Request,
    data: VerifyRequest,
    db: AsyncSession = Depends(get_db),
) -> User:
    return await AuthService(db).verify(data)