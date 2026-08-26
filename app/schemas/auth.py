"""Pydantic schemas for auth endpoints."""
from pydantic import BaseModel


class Token(BaseModel):
    """Response schema for a successful login."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Internal schema for decoded JWT payload."""
    user_id: int | None = None
