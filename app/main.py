"""
Real-World Blog API — FastAPI Application Entry Point
Assembles all 14 steps:
  1.  PostgreSQL connection via SQLAlchemy
  2.  User registration
  3.  Password hashing
  4.  JWT authentication
  5.  Blog post creation
  6.  Full CRUD operations
  7.  Author-only authorization
  8.  Comments
  9.  Pagination
  10. Search / filtering
  11. In-memory TTL caching
  12. Rate limiting (SlowAPI)
  13. .env configuration (pydantic-settings)
  14. Render deployment ready
"""
import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from app.core.config import settings
from app.database import Base, engine
from app.middleware.rate_limit import limiter
from app.routers import auth_router, posts_router, comments_router, users_router

# ─── Step 1: Create all database tables ─────────────────────────────────────
# Import models so they are registered on Base.metadata before create_all()
import app.models  # noqa: F401 — ensures all ORM models are loaded
import logging

logger = logging.getLogger(__name__)

try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created / verified successfully.")
except Exception as exc:
    logger.warning(
        f"Could not connect to the database at startup: {exc}\n"
        "The server will still start — fix DATABASE_URL in .env and restart."
    )

# ─── FastAPI App ─────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    description="""
## 🚀 Real-World Blog API

A production-grade REST API built with **FastAPI + PostgreSQL** covering:

- ✅ User registration & JWT authentication
- ✅ Blog post CRUD with author-only authorization
- ✅ Comments with pagination
- ✅ Full-text search & filtering
- ✅ In-memory TTL caching
- ✅ Rate limiting (60 req/min, 5/min on login)
- ✅ Environment-based configuration
- ✅ Ready to deploy on Render

### Authentication
Click **Authorize 🔓** and enter `Bearer <your_token>` after logging in via `/auth/login`.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "Blog API Support",
        "url": "https://github.com",
    },
    license_info={
        "name": "MIT",
    },
)

# ─── Step 12: Attach Rate Limiter ────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ─── CORS Middleware ─────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Static Files & Frontend UI ─────────────────────────────────────────────
_static_dir = "static"
if os.path.exists(_static_dir):
    app.mount("/static", StaticFiles(directory=_static_dir), name="static")


# ─── Routers ─────────────────────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(posts_router)
app.include_router(comments_router)
app.include_router(users_router)


# ─── Root: serve frontend SPA ────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
def root():
    """Serve the Blog frontend SPA at the root URL."""
    index = os.path.join(_static_dir, "index.html")
    if os.path.exists(index):
        return FileResponse(index)
    # Fallback JSON if static files aren't present (e.g. API-only deploy)
    return {
        "status": "online",
        "api": settings.APP_NAME,
        "version": "1.0.0",
        "docs": "/docs",
        "ui": "/ui",
    }


@app.get("/ui", include_in_schema=False)
def serve_ui():
    """Alias for the Blog frontend SPA."""
    return RedirectResponse(url="/", status_code=301)


# ─── API status (JSON) ────────────────────────────────────────────────────────
@app.get("/api", tags=["Health"], summary="API status (JSON)")
def api_status():
    """Returns API status as JSON."""
    return {
        "status": "online",
        "api": settings.APP_NAME,
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"], summary="Detailed health status")
def health():
    """Detailed service health status."""
    return {
        "status": "healthy",
        "database": "postgresql",
        "cache": "in-memory TTL",
        "rate_limiting": "enabled (60/min)",
    }
