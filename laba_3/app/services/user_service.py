from typing import List, Optional
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate
from sqlalchemy.ext.asyncio import AsyncSession


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Получить пользователя по ID"""
        return await self.user_repository.get_by_id(self.user_repository.session, user_id)

    async def get_by_filter(self, count: int = 10, page: int = 1, **kwargs) -> List[User]:
        """Получить пользователей по фильтру с пагинацией"""
        return await self.user_repository.get_by_filter(
            self.user_repository.session, count, page, **kwargs
        )

    async def create(self, user_data: UserCreate) -> User:
        """Создать нового пользователя"""
        # Здесь можно добавить бизнес-логику
        # Например, проверка уникальности email
        existing_user = await self.user_repository.get_by_filter(
            self.user_repository.session, email=user_data.email
        )
        if existing_user:
            raise ValueError(f"User with email {user_data.email} already exists")

        return await self.user_repository.create(self.user_repository.session, user_data)

    async def update(self, user_id: str, user_data: UserUpdate) -> Optional[User]:
        """Обновить пользователя"""
        # Бизнес-логика: проверяем существует ли пользователь
        existing_user = await self.get_by_id(user_id)
        if not existing_user:
            return None

        # Если обновляется email, проверяем уникальность
        if user_data.email and user_data.email != existing_user.email:
            user_with_email = await self.user_repository.get_by_filter(
                self.user_repository.session, email=user_data.email
            )
            if user_with_email:
                raise ValueError(f"User with email {user_data.email} already exists")

        return await self.user_repository.update(
            self.user_repository.session, user_id, user_data
        )

    async def delete(self, user_id: str) -> bool:
        """Удалить пользователя"""
        return await self.user_repository.delete(self.user_repository.session, user_id)

    async def get_total_count(self, **kwargs) -> int:
        """Получить общее количество пользователей (для задания со звездочкой)"""
        return await self.user_repository.get_total_count(
            self.user_repository.session, **kwargs
        )