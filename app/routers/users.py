"""
Users Router — Public user profile endpoints
Endpoints:
  GET /users/{user_id}        — public user profile
  GET /users/{user_id}/posts  — posts by a specific user (paginated)
"""
import math

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.post import Post
from app.schemas.user import UserOut
from app.schemas.post import PaginatedPosts

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/{user_id}",
    response_model=UserOut,
    summary="Get a user's public profile",
)
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    """Retrieve a user's public profile information."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id={user_id} not found",
        )
    return user


@router.get(
    "/{user_id}/posts",
    response_model=PaginatedPosts,
    summary="Get all posts by a specific user",
)
def get_user_posts(
    user_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Retrieve all blog posts created by a specific user (paginated)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id={user_id} not found",
        )

    query = db.query(Post).filter(Post.author_id == user_id)
    total = query.count()
    pages = math.ceil(total / limit) if total > 0 else 1
    posts = (
        query.order_by(Post.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return PaginatedPosts(total=total, page=page, limit=limit, pages=pages, items=posts)
