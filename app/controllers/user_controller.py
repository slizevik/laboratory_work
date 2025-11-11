from litestar import Controller, get, post, put, delete
from litestar.params import Parameter
from litestar.exceptions import NotFoundException
from typing import List

from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from sqlalchemy.ext.asyncio import AsyncSession


class UserController(Controller):
    path = "/users"

    @get("/{user_id:str}")
    async def get_user_by_id(
            self,
            user_service: UserService,
            db_session: AsyncSession,
            user_id: str = Parameter(description="ID пользователя")
    ) -> UserResponse:
        """Получить пользователя по ID"""
        user = await user_service.get_by_id(db_session, user_id)
        if not user:
            raise NotFoundException(detail=f"User with ID {user_id} not found")
        return UserResponse.model_validate(user)

    @get()
    async def get_all_users(
            self,
            user_service: UserService,
            db_session: AsyncSession,
            count: int = 10,
            page: int = 1
    ) -> List[UserResponse]:
        """Получить всех пользователей с пагинацией"""
        users = await user_service.get_by_filter(db_session, count, page)
        return [UserResponse.model_validate(user) for user in users]

    @post()
    async def create_user(
            self,
            user_service: UserService,
            db_session: AsyncSession,
            data: UserCreate,
    ) -> UserResponse:
        """Создать нового пользователя"""
        user = await user_service.create_user(db_session, data)
        return UserResponse.model_validate(user)

    @put("/{user_id:str}")
    async def update_user(
            self,
            user_service: UserService,
            db_session: AsyncSession,
            user_id: str,
            data: UserUpdate,
    ) -> UserResponse:
        """Обновить пользователя"""
        user = await user_service.update_user(db_session, user_id, data)
        if not user:
            raise NotFoundException(detail=f"User with ID {user_id} not found")
        return UserResponse.model_validate(user)

    @delete("/{user_id:str}")
    async def delete_user(
            self,
            user_service: UserService,
            db_session: AsyncSession,
            user_id: str,
    ) -> None:
        """Удалить пользователя"""
        success = await user_service.delete_user(db_session, user_id)
        if not success:
            raise NotFoundException(detail=f"User with ID {user_id} not found")