"""Routers package."""
from app.routers.auth import router as auth_router
from app.routers.posts import router as posts_router
from app.routers.comments import router as comments_router
from app.routers.users import router as users_router

__all__ = ["auth_router", "posts_router", "comments_router", "users_router"]
