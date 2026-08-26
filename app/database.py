"""
Step 1 — FastAPI + PostgreSQL Connection
SQLAlchemy synchronous engine, session factory, and Base declarative model.
"""
import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

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
        engine_args["pool_size"] = 10
        engine_args["max_overflow"] = 20
        
    engine = create_engine(db_url, **engine_args)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, SessionLocal


# Try to connect using the configured DATABASE_URL
db_url = settings.DATABASE_URL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

engine, SessionLocal = create_db_engine_and_session(db_url)

# Test connection and fallback if needed
try:
    with engine.connect() as conn:
        pass
except Exception as exc:
    # If the database URL is not SQLite and the connection fails, fall back to SQLite
    if not db_url.startswith("sqlite"):
        fallback_url = "sqlite:///./blog.db"
        logger.warning(
            f"Could not connect to database at {db_url}: {exc}\n"
            f"Falling back to local SQLite database: {fallback_url}"
        )
        engine, SessionLocal = create_db_engine_and_session(fallback_url)
    else:
        logger.error(f"Could not connect to SQLite database at {db_url}: {exc}")
        raise exc


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

