"""
Step 1 — FastAPI + PostgreSQL Connection
SQLAlchemy synchronous engine, session factory, and Base declarative model.
"""
import logging
import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

# All ORM models inherit from this Base
Base = declarative_base()


def create_db_engine_and_session(db_url: str):
    is_sqlite = db_url.startswith("sqlite")
    connect_args = {"check_same_thread": False} if is_sqlite else {}

    engine_args = {
        "pool_pre_ping": True,
        "connect_args": connect_args,
    }

    # pool_size and max_overflow are only supported on QueuePool (default for Postgres, not SQLite)
    if not is_sqlite:
        engine_args["pool_size"] = 5
        engine_args["max_overflow"] = 10
        engine_args["pool_timeout"] = 30

    engine = create_engine(db_url, **engine_args)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, SessionLocal


def _resolve_db_url() -> str:
    """
    Resolve the DATABASE_URL from environment / settings.
    Normalises postgres:// -> postgresql:// for SQLAlchemy 1.4+.
    Falls back to SQLite if no DATABASE_URL is set (local dev only).
    """
    # Import here to avoid circular imports during startup
    db_url = os.environ.get("DATABASE_URL", "")

    # pydantic-settings may have already loaded it; try settings as fallback
    if not db_url:
        try:
            from app.core.config import settings
            db_url = settings.DATABASE_URL
        except Exception:
            pass

    if not db_url:
        logger.warning("DATABASE_URL not set — falling back to local SQLite.")
        return "sqlite:///./blog.db"

    # Render (and Heroku) provide postgres:// which SQLAlchemy 2 rejects
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    return db_url


# ─── Build engine ────────────────────────────────────────────────────────────
_db_url = _resolve_db_url()
engine, SessionLocal = create_db_engine_and_session(_db_url)

# Test connection; fall back to SQLite only in non-production scenarios
try:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    logger.info("Database connection verified successfully.")
except Exception as exc:
    if not _db_url.startswith("sqlite"):
        fallback_url = "sqlite:///./blog.db"
        logger.warning(
            f"Could not connect to database ({exc}). "
            f"Falling back to SQLite: {fallback_url}"
        )
        engine, SessionLocal = create_db_engine_and_session(fallback_url)
    else:
        logger.error(f"Could not connect to SQLite: {exc}")
        raise


def get_db():
    """
    FastAPI dependency — yields a DB session and ensures it is closed
    after the request completes (even on error).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
