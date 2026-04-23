import os
import uuid
from enum import Enum
from typing import Optional

from fastapi import Depends
from fastapi_users import BaseUserManager, UUIDIDMixin, schemas
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from sqlalchemy import Column, String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session


class Base(DeclarativeBase):
    pass


class Role(str, Enum):
    user = "user"
    admin = "admin"


class User(SQLAlchemyBaseUserTableUUID, Base):
    role: str = Column(String, nullable=False, default=Role.user)


# Pydantic sheme
class UserRead(schemas.BaseUser[uuid.UUID]):
    role: str

class UserCreate(schemas.BaseUserCreate):
    role: str = Role.user

class UserUpdate(schemas.BaseUserUpdate):
    role: Optional[str] = None


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = os.getenv("SECRET_KEY", "fallback-dev-secret")
    verification_token_secret = os.getenv("SECRET_KEY", "fallback-dev-secret")

    async def on_after_register(self, user: User, request=None):
        print(f"[AUTH] Novi korisnik registrovan: {user.email}")

    async def on_after_login(self, user: User, request=None, response=None):
        print(f"[AUTH] Korisnik se prijavio: {user.email}")


async def get_user_db(session: AsyncSession = Depends(get_session)):
    yield SQLAlchemyUserDatabase(session, User)


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)