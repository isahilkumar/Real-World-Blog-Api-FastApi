"""Pydantic schemas for Post endpoints."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator, ConfigDict

from app.schemas.user import UserProfile


class PostCreate(BaseModel):
    """Body for POST /posts/."""
    title: str
    content: str
    summary: Optional[str] = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Title cannot be empty")
        if len(v) > 255:
            raise ValueError("Title must be at most 255 characters")
        return v

    @field_validator("content")
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Content cannot be empty")
        return v


class PostUpdate(BaseModel):
    """Body for PUT /posts/{id} — all fields optional."""
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None


class PostOut(BaseModel):
    """Full post response including author info."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    summary: Optional[str]
    author_id: int
    author: UserProfile
    created_at: datetime
    updated_at: datetime


class PostSummaryOut(BaseModel):
    """Lightweight post representation for list endpoints."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    summary: Optional[str]
    author: UserProfile
    created_at: datetime
    updated_at: datetime


class PaginatedPosts(BaseModel):
    """Paginated posts list response."""
    total: int
    page: int
    limit: int
    pages: int
    items: list[PostSummaryOut]
