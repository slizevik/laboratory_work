import os
from litestar import Litestar
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.controllers.user_controller import UserController
from app.dependencies import provide_user_repository, provide_user_service

# Настройка базы данных - ИСПОЛЬЗУЕМ ТВОИ ДАННЫЕ ИЗ ЛР2
DATABASE_URL = "postgresql+asyncpg://postgres:postgres@192.168.99.100:5432/postgres"

# Создаем асинхронный движок БД
engine = create_async_engine(DATABASE_URL, echo=True)
async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def provide_db_session() -> AsyncSession:
    """Провайдер сессии базы данных"""
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


# Создаем приложение Litestar
app = Litestar(
    route_handlers=[UserController],  # Регистрируем наш контроллер
    dependencies={
        "db_session": provide_db_session,
        "user_repository": provide_user_repository,
        "user_service": provide_user_service,
    },
)

if __name__ == "__main__":
    import uvicorn

    print("Запускаем веб-приложение на http://localhost:8000")
    print("Доступные endpoints:")
    print("   GET    /users          - список всех пользователей")
    print("   GET    /users/{id}     - пользователь по ID")
    print("   POST   /users          - создать пользователя")
    print("   PUT    /users/{id}     - обновить пользователя")
    print("   DELETE /users/{id}     - удалить пользователя")
    print("\nДля остановки Ctrl+C")

    uvicorn.run(app, host="0.0.0.0", port=8000)