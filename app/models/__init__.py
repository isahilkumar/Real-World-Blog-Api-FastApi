"""Models package — import all models here so SQLAlchemy metadata is populated."""
from app.models.user import User
from app.models.post import Post
from app.models.comment import Comment

__all__ = ["User", "Post", "Comment"]
