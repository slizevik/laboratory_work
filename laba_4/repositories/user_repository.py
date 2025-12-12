# repositories/user_repository.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from models import User
from schemas.user import UserCreate, UserUpdate


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session  

    async def get_by_id(self, user_id: str) -> Optional[User]:  
        """Получить пользователя по ID"""
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_filter(self, count: int = 10, page: int = 1, **kwargs) -> List[User]:  
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

        result = await self.session.execute(query)
        return result.scalars().all()

    async def create(self, user_data: UserCreate) -> User:  
        """Создать нового пользователя"""
        user = User(
            username=user_data.username,
            email=user_data.email
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update(self, user_id: str, user_data: UserUpdate) -> Optional[User]:  
        """Обновить пользователя"""
        user = await self.get_by_id(user_id)
        if not user:
            return None

        # Обновляем только переданные поля
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(user, field):
                setattr(user, field, value)

        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete(self, user_id: str) -> bool:  
        """Удалить пользователя"""
        user = await self.get_by_id(user_id)
        if not user:
            return False

        await self.session.delete(user)
        await self.session.commit()
        return True

    async def get_total_count(self, **kwargs) -> int:  
        """Получить общее количество пользователей (для задания со звездочкой)"""
        query = select(User)

        # Применяем фильтры
        if kwargs:
            for key, value in kwargs.items():
                if hasattr(User, key) and value is not None:
                    query = query.where(getattr(User, key) == value)

        result = await self.session.execute(query)
        return len(result.scalars().all())