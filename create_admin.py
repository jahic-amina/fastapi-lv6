"""
Pokreni jednom:  python create_admin.py
"""
import uuid
import asyncio
from sqlalchemy import select
from fastapi_users.password import PasswordHelper

from database import engine, create_db_and_tables
from auth.users import User, Role, Base


async def create_admin():
    await create_db_and_tables()
    helper = PasswordHelper()

    from sqlalchemy.ext.asyncio import AsyncSession
    async with AsyncSession(engine) as session:
        result = await session.execute(select(User).where(User.email == "admin@fet.ba"))
        existing = result.scalars().first()

        if existing:
            print("Admin već postoji! Email: admin@fet.ba")
            return

        admin = User(
            id=uuid.uuid4(),
            email="admin@fet.ba",
            hashed_password=helper.hash("admin123"),
            is_active=True,
            is_verified=True,
            is_superuser=False,
            role=Role.admin,
        )
        session.add(admin)
        await session.commit()
        print("✓ Admin kreiran!")
        print("  Email:    admin@fet.ba")
        print("  Lozinka:  admin123")


if __name__ == "__main__":
    asyncio.run(create_admin())