import os
from litestar import Litestar
from litestar.di import Provide
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker


from app.controllers.user_controller import UserController
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService


DATABASE_URL = "postgresql+asyncpg://postgres:postgres@192.168.99.100:5432/postgres"

# асинхронный движок БД
engine = create_async_engine(DATABASE_URL, echo=True)

# Создаем фабрику сессий
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def provide_db_session() -> AsyncSession:
    """Провайдер сессии базы данных"""
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()

async def provide_user_repository(db_session: AsyncSession) -> UserRepository:
    """Провайдер репозитория пользователей"""
    return UserRepository(db_session)

async def provide_user_service(user_repository: UserRepository) -> UserService:
    """Провайдер сервиса пользователей"""
    return UserService(user_repository)

# Создаем приложение Litestar
app = Litestar(
    route_handlers=[UserController],
    dependencies={
        "db_session": Provide(provide_db_session),
        "user_repository": Provide(provide_user_repository),
        "user_service": Provide(provide_user_service),
    },
)

if __name__ == "__main__":
    import uvicorn
    print("Запуск Litestar приложения на http://0.0.0.0:8000")
    print("Доступные эндпоинты:")
    print("  GET    /users - список пользователей")
    print("  POST   /users - создать пользователя")
    print("  GET    /users/{id} - получить пользователя по ID")
    print("  PUT    /users/{id} - обновить пользователя")
    print("  DELETE /users/{id} - удалить пользователя")
    uvicorn.run(app, host="0.0.0.0", port=8000)