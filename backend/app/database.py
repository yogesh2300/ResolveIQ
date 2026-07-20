"""SQLAlchemy engine, session, and FastAPI DB dependency for DeskPilot."""

from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeMeta, Session, declarative_base, sessionmaker

# backend/app/database.py -> project root (DeskPilot/)
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent.parent

load_dotenv(PROJECT_ROOT / ".env")

DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./backend/deskpilot.db")

# SQLite needs check_same_thread=False for FastAPI's multi-threaded request handling.
# PostgreSQL and other backends do not accept this argument.
connect_args: dict[str, Any] = (
    {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

engine: Engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base: DeclarativeMeta = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Yield a DB session and always close it when the request finishes."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
