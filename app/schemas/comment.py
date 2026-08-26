"""Pydantic schemas for Comment endpoints."""
from datetime import datetime
from pydantic import BaseModel, field_validator, ConfigDict

from app.schemas.user import UserProfile


class CommentCreate(BaseModel):
    """Body for POST /posts/{id}/comments."""
    content: str

    @field_validator("content")
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Comment content cannot be empty")
        if len(v) > 2000:
            raise ValueError("Comment must be at most 2000 characters")
        return v


class CommentOut(BaseModel):
    """Full comment response."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    content: str
    post_id: int
    author: UserProfile
    created_at: datetime


class PaginatedComments(BaseModel):
    """Paginated comments list response."""
    total: int
    page: int
    limit: int
    pages: int
    items: list[CommentOut]
