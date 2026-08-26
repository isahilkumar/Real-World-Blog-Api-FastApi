"""
Step 8 & 9 — Comments Router
Endpoints:
  POST   /posts/{post_id}/comments   — add comment (auth required)
  GET    /posts/{post_id}/comments   — list comments (paginated, cached)
  DELETE /comments/{comment_id}      — delete own comment
"""
import math

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.comment import Comment
from app.models.post import Post
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentOut, PaginatedComments
from app.core.dependencies import get_current_user
from app.core import cache as cache_store

router = APIRouter(tags=["Comments"])


# ─── Step 8: Add Comment ─────────────────────────────────────────────────────
@router.post(
    "/posts/{post_id}/comments",
    response_model=CommentOut,
    status_code=status.HTTP_201_CREATED,
    summary="Add a comment to a post",
)
def add_comment(
    post_id: int,
    comment_in: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a comment to a specific blog post. Requires authentication."""
    # Verify the post exists
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id={post_id} not found",
        )

    comment = Comment(
        content=comment_in.content,
        post_id=post_id,
        author_id=current_user.id,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    # Step 11 — Invalidate comments cache for this post
    cache_store.invalidate_comments_cache(post_id)
    return comment


# ─── Step 8 + 9: List Comments (paginated, cached) ───────────────────────────
@router.get(
    "/posts/{post_id}/comments",
    response_model=PaginatedComments,
    summary="Get paginated comments for a post",
)
def list_comments(
    post_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
):
    """
    Retrieve paginated comments for a specific post.
    - **page**: page number (default 1)
    - **limit**: items per page (1–100, default 20)
    
    Results are cached for 60 seconds.
    """
    # Verify post exists
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id={post_id} not found",
        )

    # Step 11 — Check cache
    cache_key = f"comments:{post_id}:page:{page}:limit:{limit}"
    cached = cache_store.get_cached(cache_store.comments_cache, cache_key)
    if cached is not None:
        return cached

    # Step 9: Pagination
    query = db.query(Comment).filter(Comment.post_id == post_id)
    total = query.count()
    pages = math.ceil(total / limit) if total > 0 else 1
    comments = (
        query.order_by(Comment.created_at.asc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    result = PaginatedComments(
        total=total,
        page=page,
        limit=limit,
        pages=pages,
        items=comments,
    )

    # Step 11 — Cache the result
    cache_store.set_cached(cache_store.comments_cache, cache_key, result)
    return result


# ─── Step 8: Delete Comment (Author Only) ────────────────────────────────────
@router.delete(
    "/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a comment (author only)",
)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a comment. Only the comment author can perform this action."""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comment with id={comment_id} not found",
        )

    if comment.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this comment",
        )

    post_id = comment.post_id
    db.delete(comment)
    db.commit()

    # Step 11 — Invalidate cache
    cache_store.invalidate_comments_cache(post_id)
