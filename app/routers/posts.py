"""
Steps 5, 6, 7, 9, 10, 11 — Posts Router
Endpoints:
  POST   /posts/              — create post (auth required)
  GET    /posts/              — list posts (paginated + searchable, cached)
  GET    /posts/{id}          — get single post (cached)
  PUT    /posts/{id}          — update post (author only)
  DELETE /posts/{id}          — delete post (author only)
"""
import math
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.post import Post
from app.models.user import User
from app.schemas.post import PostCreate, PostUpdate, PostOut, PaginatedPosts
from app.core.dependencies import get_current_user
from app.core import cache as cache_store

router = APIRouter(prefix="/posts", tags=["Posts"])


# ─── Step 5: Create Post ─────────────────────────────────────────────────────
@router.post(
    "/",
    response_model=PostOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new blog post",
)
def create_post(
    post_in: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new blog post. Requires authentication."""
    post = Post(
        title=post_in.title,
        content=post_in.content,
        summary=post_in.summary,
        author_id=current_user.id,
    )
    db.add(post)
    db.commit()
    db.refresh(post)

    # Step 11 — Invalidate list cache after new post
    cache_store.invalidate_posts_cache()
    return post


# ─── Step 6 + 9 + 10: List Posts (paginated + search + filter) ──────────────
@router.get(
    "/",
    response_model=PaginatedPosts,
    summary="List blog posts with pagination and search",
)
def list_posts(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search in title and content"),
    author_id: Optional[int] = Query(None, description="Filter by author ID"),
    db: Session = Depends(get_db),
):
    """
    Retrieve a paginated list of blog posts.
    - **page**: page number (default 1)
    - **limit**: items per page (1–100, default 10)
    - **search**: full-text search on title + content
    - **author_id**: filter by a specific author
    
    Results are cached for 60 seconds.
    """
    # Step 11 — Check cache first
    cache_key = cache_store.make_cache_key("posts_list", page, limit, search, author_id)
    cached = cache_store.get_cached(cache_store.posts_cache, cache_key)
    if cached is not None:
        return cached

    # Build query
    query = db.query(Post)

    # Step 10: Search filter
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            Post.title.ilike(search_term) | Post.content.ilike(search_term)
        )

    # Step 10: Author filter
    if author_id:
        query = query.filter(Post.author_id == author_id)

    # Step 9: Pagination
    total = query.count()
    pages = math.ceil(total / limit) if total > 0 else 1
    posts = (
        query.order_by(Post.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    result = PaginatedPosts(
        total=total,
        page=page,
        limit=limit,
        pages=pages,
        items=posts,
    )

    # Step 11 — Cache the result
    cache_store.set_cached(cache_store.posts_cache, cache_key, result)
    return result


# ─── Step 6: Get Single Post ─────────────────────────────────────────────────
@router.get(
    "/{post_id}",
    response_model=PostOut,
    summary="Get a single post by ID",
)
def get_post(post_id: int, db: Session = Depends(get_db)):
    """Retrieve a single blog post. Response is cached for 120 seconds."""
    # Step 11 — Check cache
    cached = cache_store.get_cached(cache_store.post_detail_cache, str(post_id))
    if cached is not None:
        return cached

    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id={post_id} not found",
        )

    # Step 11 — Cache the post
    cache_store.set_cached(cache_store.post_detail_cache, str(post_id), post)
    return post


# ─── Step 6 + 7: Update Post (Author Only) ───────────────────────────────────
@router.put(
    "/{post_id}",
    response_model=PostOut,
    summary="Update a post (author only)",
)
def update_post(
    post_id: int,
    post_in: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a blog post. Only the post author can perform this action.
    All fields are optional — only provided fields will be updated.
    """
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id={post_id} not found",
        )

    # Step 7 — Authorization: only author can edit
    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to edit this post",
        )

    # Apply partial updates (only provided fields)
    update_data = post_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(post, field, value)

    db.commit()
    db.refresh(post)

    # Step 11 — Invalidate caches
    cache_store.invalidate_post_cache(post_id)
    return post


# ─── Step 6 + 7: Delete Post (Author Only) ───────────────────────────────────
@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a post (author only)",
)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a blog post. Only the post author can perform this action.
    All associated comments are also deleted (cascade).
    """
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id={post_id} not found",
        )

    # Step 7 — Authorization: only author can delete
    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this post",
        )

    db.delete(post)
    db.commit()

    # Step 11 — Invalidate caches
    cache_store.invalidate_post_cache(post_id)
