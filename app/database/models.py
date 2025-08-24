"""
Async database models and engine setup for managing authorized and blacklisted users.

This module provides:
- SQLAlchemy async engine and session setup
- Base declarative models
- Tables for authorized and blacklisted users

All database operations should be performed using async sessions.
"""

import asyncio
import os
import sys
from loguru import logger
from dotenv import load_dotenv
from sqlalchemy import BigInteger, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

load_dotenv()
logger.add("logs/log.log", rotation="1 day", level="INFO", enqueue=True)

engine = create_async_engine(
    url=f"postgresql+psycopg://{os.getenv("POSTGRES_USER")}:{os.getenv("POSTGRES_PASSWORD")}@{os.getenv("POSTGRES_HOST")}:{os.getenv("POSTGRES_PORT")}/{os.getenv("POSTGRES_DB")}")

async_session = async_sessionmaker(engine)

# Special windows event loop policy for asynchronous work with postgres
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class Base(AsyncAttrs, DeclarativeBase):
    """Base class for all database models."""
    pass


class AuthorizedUser(Base):
    """Represents an authorized user in the database."""
    __tablename__ = "authorized_users"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id = mapped_column(BigInteger)
    coins: Mapped[int] = mapped_column()
    timestamp = mapped_column(DateTime(timezone=True))


class BlacklistedUser(Base):
    """Represents a blacklisted user in the database."""
    __tablename__ = "blacklisted_users"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id = mapped_column(BigInteger)
    timestamp = mapped_column(DateTime(timezone=True))


async def async_main() -> None:
    """Create all tables in the database if they do not exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Created tables in database")
