# services/user_service.py
import json
from typing import List, Optional
from redis.asyncio import Redis

from models import User
from repositories.user_repository import UserRepository
from schemas.user import UserCreate, UserUpdate, UserResponse


USER_CACHE_TTL_SECONDS = 3600  # 1 час
USER_CACHE_KEY_PREFIX = "cache:user:"


class UserService:
    def __init__(self, user_repository: UserRepository, redis_client: Redis):
        self.user_repository = user_repository
        self.redis = redis_client

    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Получить пользователя по ID (с кэшированием в Redis)"""
        cache_key = f"{USER_CACHE_KEY_PREFIX}{user_id}"

        # 1) Проверяем кэш
        cached = await self.redis.get(cache_key)
        if cached:
            data = json.loads(cached)
            return UserResponse(**data)

        # 2) Иначе читаем из БД
        user = await self.user_repository.get_by_id(user_id)
        if user:
            # Сериализуем в dict и кладём в кэш
            payload = UserResponse.model_validate(user).model_dump()
            await self.redis.set(cache_key, json.dumps(payload), ex=USER_CACHE_TTL_SECONDS)
        return user

    async def get_by_filter(self, count: int = 10, page: int = 1, **kwargs) -> List[User]:
        """Получить пользователей по фильтру с пагинацией"""
        return await self.user_repository.get_by_filter(count, page, **kwargs)

    async def create(self, user_data: UserCreate) -> User:
        """Создать нового пользователя"""
        # Здесь можно добавить бизнес-логику
        # Например, проверка уникальности email
        existing_users = await self.user_repository.get_by_filter(email=user_data.email)
        if existing_users:
            raise ValueError(f"User with email {user_data.email} already exists")

        return await self.user_repository.create(user_data)

    async def update(self, user_id: str, user_data: UserUpdate) -> Optional[User]:
        """Обновить пользователя"""
        # Бизнес-логика: проверяем существует ли пользователь
        existing_user = await self.get_by_id(user_id)
        if not existing_user:
            return None

        # Если обновляется email, проверяем уникальность
        if user_data.email and user_data.email != existing_user.email:
            user_with_email = await self.user_repository.get_by_filter(email=user_data.email)
            if user_with_email:
                raise ValueError(f"User with email {user_data.email} already exists")

        updated = await self.user_repository.update(user_id, user_data)

        # После обновления инвалидируем кэш
        cache_key = f"{USER_CACHE_KEY_PREFIX}{user_id}"
        await self.redis.delete(cache_key)
        return updated

    async def delete(self, user_id: str) -> bool:
        """Удалить пользователя"""
        deleted = await self.user_repository.delete(user_id)
        if deleted:
            cache_key = f"{USER_CACHE_KEY_PREFIX}{user_id}"
            await self.redis.delete(cache_key)
        return deleted

    async def get_total_count(self, **kwargs) -> int:
        """Получить общее количество пользователей (для задания со звездочкой)"""
        return await self.user_repository.get_total_count(**kwargs)