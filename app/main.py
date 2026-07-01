from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.core.config import settings

# Rate limiter instance — uses the client's IP address as the key.
# This is attached to app.state so slowapi can find it automatically.
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Users API — registration, authentication, verification and user management.",
)

# CORS — restrict which origins can call our API.
# In production this should be set to the exact frontend domain(s).
# With more time this would be loaded from environment variables so it
# can be configured per environment without code changes.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.ENVIRONMENT == "dev" else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware and error handler.
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(auth_router)
app.include_router(users_router)


@app.get("/health", tags=["health 🍀"], summary="Health check")
async def health_check() -> dict[str, str]:
    """Simple liveness probe used to verify the service is running."""
    return {"status": "ok"}