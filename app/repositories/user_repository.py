from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import User  # Импортируем твою модель из ЛР2
from app.schemas.user import UserCreate, UserUpdate
from typing import List, Optional


class UserRepository:

    async def get_by_id(self, session: AsyncSession, user_id: str) -> Optional[User]:
        """Найти пользователя по ID"""
        result = await session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_filter(
            self,
            session: AsyncSession,
            count: int = 10,
            page: int = 1,
            **kwargs
    ) -> List[User]:
        """Найти пользователей с фильтрацией и пагинацией"""
        query = select(User)

        # Фильтрация по переданным параметрам
        for key, value in kwargs.items():
            if hasattr(User, key) and value is not None:
                query = query.where(getattr(User, key) == value)

        # Пагинация
        offset = (page - 1) * count
        query = query.offset(offset).limit(count)

        result = await session.execute(query)
        return list(result.scalars().all())

    async def create(self, session: AsyncSession, user_data: UserCreate) -> User:
        """Создать нового пользователя"""
        user = User(
            username=user_data.username,
            email=user_data.email
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    async def update(
            self,
            session: AsyncSession,
            user_id: str,
            user_data: UserUpdate
    ) -> Optional[User]:
        """Обновить пользователя"""
        user = await self.get_by_id(session, user_id)
        if not user:
            return None

        # Обновляем только переданные поля
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        await session.commit()
        await session.refresh(user)
        return user

    async def delete(self, session: AsyncSession, user_id: str) -> bool:
        """Удалить пользователя"""
        user = await self.get_by_id(session, user_id)
        if not user:
            return False

        await session.delete(user)
        await session.commit()
        return True

    async def get_total_count(self, session: AsyncSession) -> int:
        """Получить общее количество пользователей"""
        result = await session.execute(select(User))
        return len(result.scalars().all())