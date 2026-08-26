"""
Step 11 — Caching
Simple in-memory TTL cache using cachetools. No Redis required.
Cache is invalidated on any write operation to the affected resource.
"""
from cachetools import TTLCache
from typing import Any, Optional
import hashlib
import json

# ─── Cache Stores ────────────────────────────────────────────────────────────
# Posts list cache: up to 100 entries, each lives 60 seconds
posts_cache: TTLCache = TTLCache(maxsize=100, ttl=60)

# Single post cache: up to 500 entries, each lives 120 seconds
post_detail_cache: TTLCache = TTLCache(maxsize=500, ttl=120)

# Comments cache: up to 500 entries, each lives 60 seconds
comments_cache: TTLCache = TTLCache(maxsize=500, ttl=60)


def make_cache_key(*args, **kwargs) -> str:
    """Generate a stable string cache key from arbitrary arguments."""
    raw = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
    return hashlib.md5(raw.encode()).hexdigest()


def get_cached(cache: TTLCache, key: str) -> Optional[Any]:
    """Retrieve a value from cache; returns None on miss."""
    return cache.get(key)


def set_cached(cache: TTLCache, key: str, value: Any) -> None:
    """Store a value in the cache."""
    cache[key] = value


def invalidate_posts_cache() -> None:
    """Clear the entire posts list cache (call after create/update/delete)."""
    posts_cache.clear()


def invalidate_post_cache(post_id: int) -> None:
    """Remove a single post from the detail cache."""
    post_detail_cache.pop(str(post_id), None)
    # Also clear list cache since list results are affected
    posts_cache.clear()


def invalidate_comments_cache(post_id: int) -> None:
    """Remove all comment entries for a post."""
    keys_to_delete = [k for k in comments_cache if k.startswith(f"comments:{post_id}")]
    for k in keys_to_delete:
        comments_cache.pop(k, None)
