from pydantic import BaseModel


class TokenPair(BaseModel):
    """Schema returned after a successful login: a pair of JWT tokens."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AccessToken(BaseModel):
    """Schema returned after refreshing an access token."""

    access_token: str
    token_type: str = "bearer"