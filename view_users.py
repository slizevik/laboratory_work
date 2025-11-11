import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from models import User


async def view_all_users():
    print("ВСЕ ПОЛЬЗОВАТЕЛИ В БАЗЕ ДАННЫХ")

    DATABASE_URL = "postgresql+asyncpg://postgres:postgres@192.168.99.100:5432/postgres"
    engine = create_async_engine(DATABASE_URL, echo=False)  # echo=False чтобы меньше логов
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()

        print(f"Всего пользователей: {len(users)}")


        for i, user in enumerate(users, 1):
            print(f"{i}. ID: {user.id}")
            print(f"   Username: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   Description: {user.description}")
            print(f"   Created: {user.created_at}")



if __name__ == "__main__":
    asyncio.run(view_all_users())