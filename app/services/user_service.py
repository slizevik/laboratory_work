from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate
from models import User
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession


class UserService:

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def get_by_id(self, session: AsyncSession, user_id: str) -> Optional[User]:
        return await self.user_repository.get_by_id(session, user_id)

    async def get_by_filter(self, session: AsyncSession, count: int = 10, page: int = 1, **kwargs) -> List[User]:
        return await self.user_repository.get_by_filter(session, count, page, **kwargs)

    async def create_user(self, session: AsyncSession, user_data: UserCreate) -> User:
        # Проверяем уникальность email
        existing_users = await self.user_repository.get_by_filter(session, email=user_data.email)
        if existing_users:
            raise ValueError(f"User with email {user_data.email} already exists")

        # Проверяем уникальность username
        existing_users = await self.user_repository.get_by_filter(session, username=user_data.username)
        if existing_users:
            raise ValueError(f"User with username {user_data.username} already exists")

        return await self.user_repository.create(session, user_data)

    async def update_user(self, session: AsyncSession, user_id: str, user_data: UserUpdate) -> Optional[User]:
        user = await self.get_by_id(session, user_id)
        if not user:
            return None

        # Проверяем уникальность email если он обновляется
        if user_data.email is not None:
            existing_users = await self.user_repository.get_by_filter(session, email=user_data.email)
            existing_users = [u for u in existing_users if u.id != user_id]
            if existing_users:
                raise ValueError(f"User with email {user_data.email} already exists")

        # Проверяем уникальность username если он обновляется
        if user_data.username is not None:
            existing_users = await self.user_repository.get_by_filter(session, username=user_data.username)
            existing_users = [u for u in existing_users if u.id != user_id]
            if existing_users:
                raise ValueError(f"User with username {user_data.username} already exists")

        return await self.user_repository.update(session, user_id, user_data)

    async def delete_user(self, session: AsyncSession, user_id: str) -> bool:
        return await self.user_repository.delete(session, user_id)

    async def get_total_count(self, session: AsyncSession) -> int:
        return await self.user_repository.get_total_count(session)