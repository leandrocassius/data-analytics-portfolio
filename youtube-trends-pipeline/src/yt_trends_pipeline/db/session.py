"""Database engine and session factory from DATABASE_URL."""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .models import Base

_engine = None
_SessionLocal = None


def get_engine(database_url: str | None = None):
    """Create or return the global SQLAlchemy engine."""
    global _engine
    if _engine is None:
        url = database_url or _get_database_url()
        _engine = create_engine(url, pool_pre_ping=True)
    return _engine


def _get_database_url() -> str:
    from ..config import get_settings
    return get_settings().database_url


def get_session_factory(database_url: str | None = None):
    """Return a session factory bound to the engine."""
    global _SessionLocal
    if _SessionLocal is None:
        engine = get_engine(database_url)
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return _SessionLocal


@contextmanager
def get_session(database_url: str | None = None) -> Generator[Session, None, None]:
    """Context manager yielding a database session (commit on success, rollback on error)."""
    factory = get_session_factory(database_url)
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def create_all_tables(database_url: str | None = None) -> None:
    """Create all tables defined in models (idempotent)."""
    engine = get_engine(database_url)
    Base.metadata.create_all(bind=engine)
