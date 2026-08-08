"""Database engine, sessions, and initialization helpers."""

from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session

from backend.app.config import get_settings


class Base(DeclarativeBase):
    """Base class shared by all SQLAlchemy models."""


@lru_cache
def get_engine() -> Engine:
    """Create one SQLAlchemy engine for the configured PostgreSQL database."""

    database_url = get_settings().database_url
    if not database_url:
        raise RuntimeError("DATABASE_URL is not configured")

    return create_engine(database_url, pool_pre_ping=True)


def get_db() -> Generator[Session, None, None]:
    """Provide one database session for the duration of an API request."""

    with Session(get_engine()) as session:
        yield session


def create_tables() -> None:
    """Create tables that do not already exist for this learning project."""

    from backend.app import models  # noqa: F401

    Base.metadata.create_all(bind=get_engine())
