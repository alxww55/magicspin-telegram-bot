import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy import BigInteger, String, ForeignKey, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

load_dotenv()

engine = create_async_engine(
    url=f"postgresql+psycopg://{os.getenv("POSTGRES_USER")}:{os.getenv("POSTGRES_PASSWORD")}@{os.getenv("POSTGRES_HOST")}:{os.getenv("POSTGRES_PORT")}/{os.getenv("POSTGRES_DB")}")

async_session = async_sessionmaker(engine)
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class Base(AsyncAttrs, DeclarativeBase):
    pass


class UnauthorizedUser(Base):
    __tablename__ = "unauthorized_users"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id = mapped_column(BigInteger)
    timestamp = mapped_column(DateTime(timezone=True))


class AuthorizedUser(Base):
    __tablename__ = "authorized_users"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id = mapped_column(BigInteger)
    coins: Mapped[int] = mapped_column()
    timestamp = mapped_column(DateTime(timezone=True))


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
