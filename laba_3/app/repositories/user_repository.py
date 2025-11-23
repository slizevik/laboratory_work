from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from models.user import User
from schemas.user import UserCreate, UserUpdate


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, session: AsyncSession, user_id: int) -> Optional[User]:
        """Получить пользователя по ID"""
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_filter(self, session: AsyncSession, count: int = 10, page: int = 1, **kwargs) -> List[User]:
        """Получить пользователей по фильтру с пагинацией"""
        query = select(User)

        # Применяем фильтры
        if kwargs:
            for key, value in kwargs.items():
                if hasattr(User, key) and value is not None:
                    query = query.where(getattr(User, key) == value)

        # Применяем пагинацию
        offset = (page - 1) * count
        query = query.offset(offset).limit(count)

        result = await session.execute(query)
        return result.scalars().all()

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

    async def update(self, session: AsyncSession, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Обновить пользователя"""
        user = await self.get_by_id(session, user_id)
        if not user:
            return None

        # Обновляем только переданные поля
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(user, field):
                setattr(user, field, value)

        await session.commit()
        await session.refresh(user)
        return user

    async def delete(self, session: AsyncSession, user_id: int) -> bool:
        """Удалить пользователя"""
        user = await self.get_by_id(session, user_id)
        if not user:
            return False

        await session.delete(user)
        await session.commit()
        return True

    async def get_total_count(self, session: AsyncSession, **kwargs) -> int:
        """Получить общее количество пользователей (для задания со звездочкой)"""
        query = select(User)

        # Применяем фильтры
        if kwargs:
            for key, value in kwargs.items():
                if hasattr(User, key) and value is not None:
                    query = query.where(getattr(User, key) == value)

        result = await session.execute(query)
        return len(result.scalars().all())