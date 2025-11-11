import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from models import User
import uuid
from datetime import datetime


async def test_direct_db():
    print("РАБОТА С БАЗОЙ ДАННЫХ")

    DATABASE_URL = "postgresql+asyncpg://postgres:postgres@192.168.99.100:5432/postgres"
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # 1. Посмотрим сколько пользователей сейчас в БД
        result = await session.execute(select(User))
        current_users = result.scalars().all()
        print(f"Сейчас пользователей в БД: {len(current_users)}")

        # 2. Создаем нового пользователя напрямую
        new_user = User(
            id=uuid.uuid4(),
            username="direct_user",
            email="direct@example.com",
            description="Создан напрямую через SQLAlchemy"
        )

        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

        print(f"CОЗДАН ПОЛЬЗОВАТЕЛЬ:")
        print(f"   ID: {new_user.id}")
        print(f"   Username: {new_user.username}")
        print(f"   Email: {new_user.email}")

        # 3. Проверим что пользователь добавился
        result = await session.execute(select(User))
        updated_users = result.scalars().all()
        print(f"пользователей в БД: {len(updated_users)}")


if __name__ == "__main__":
    asyncio.run(test_direct_db())