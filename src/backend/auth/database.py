import datetime
from typing import AsyncGenerator

from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from fastapi_users_db_sqlalchemy.access_token import (
    SQLAlchemyAccessTokenDatabase,
    SQLAlchemyBaseAccessTokenTable,
)
from sqlalchemy import String, Boolean, Column, Integer, TIMESTAMP, ForeignKey
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr

from fastapi_users_db_sqlalchemy.generics import GUID, TIMESTAMPAware, now_utc

# DATABASE_URL = "sqlite+aiosqlite:///../../res/web_content/semantle_ru.db"
DATABASE_URL = "sqlite+aiosqlite:///./semantle_ru.db"


class Base(DeclarativeBase):
    pass


class User(SQLAlchemyBaseUserTable[int], Base):

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    username = Column(String, nullable=False)
    registered_at = Column(TIMESTAMP, default=datetime.datetime.now(datetime.timezone.utc))
    hashed_password: Mapped[str] = mapped_column(
        String(length=1024), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )   


class AccessToken(SQLAlchemyBaseAccessTokenTable[int], Base):

    token: Mapped[str] = mapped_column(String(length=43), primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMPAware(timezone=True), index=True, nullable=False, default=now_utc
    )
    @declared_attr
    def user_id(cls) -> Mapped[int]:
        return mapped_column(Integer, ForeignKey("user.id", ondelete="cascade"), nullable=False)


engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)



#Не используем так как есть alembic

# async def create_db_and_tables():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)


async def get_access_token_db(
    session: AsyncSession = Depends(get_async_session),
):  
    yield SQLAlchemyAccessTokenDatabase(session, AccessToken)