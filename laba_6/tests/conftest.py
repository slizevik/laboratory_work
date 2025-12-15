# tests/conftest.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from litestar import Litestar
from litestar.testing import TestClient
from typing import AsyncGenerator

from models import Base
from controllers.user_controller import UserController
from controllers.product_controller import ProductController
from controllers.order_controller import OrderController
from repositories.user_repository import UserRepository
from repositories.product_repository import ProductRepository
from repositories.order_repository import OrderRepository
from services.user_service import UserService
from services.product_service import ProductService
from services.order_service import OrderService

# ===== ФИКСТУРА: ТЕСТОВАЯ БД (SQLite in-memory) =====
@pytest.fixture(scope="function")
async def test_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Создаёт тестовую БД в памяти для каждого теста."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    async with async_session_factory() as session:
        yield session

    await engine.dispose()

# ===== ФИКСТУРЫ: РЕПОЗИТОРИИ И СЕРВИСЫ =====
@pytest.fixture(scope="function")
def user_repository(test_db_session: AsyncSession) -> UserRepository:
    return UserRepository(test_db_session)

@pytest.fixture(scope="function")
def product_repository(test_db_session: AsyncSession) -> ProductRepository:
    return ProductRepository(test_db_session)

@pytest.fixture(scope="function")
def order_repository(test_db_session: AsyncSession) -> OrderRepository:
    return OrderRepository(test_db_session)

@pytest.fixture(scope="function")
def user_service(user_repository: UserRepository) -> UserService:
    return UserService(user_repository)

@pytest.fixture(scope="function")
def product_service(product_repository: ProductRepository) -> ProductService:
    return ProductService(product_repository)

@pytest.fixture(scope="function")
def order_service(
    order_repository: OrderRepository,
    product_repository: ProductRepository,
    user_repository: UserRepository,
) -> OrderService:
    return OrderService(order_repository, product_repository, user_repository)

# ===== ФИКСТУРА: ТЕСТОВОЕ ПРИЛОЖЕНИЕ LITESTAR С ПЕРЕОПРЕДЕЛЁННЫМИ ЗАВИСИМОСТЯМИ =====
@pytest.fixture(scope="function")
def test_app(
    user_repository: UserRepository,
    product_repository: ProductRepository,
    order_repository: OrderRepository,
    user_service: UserService,
    product_service: ProductService,
    order_service: OrderService,
) -> Litestar:
    """Создаёт тестовое приложение Litestar с подменёнными зависимостями."""

    # Функции-провайдеры, которые возвращают нужные объекты
    def provide_user_repository() -> UserRepository:
        return user_repository

    def provide_product_repository() -> ProductRepository:
        return product_repository

    def provide_order_repository() -> OrderRepository:
        return order_repository

    def provide_user_service() -> UserService:
        return user_service

    def provide_product_service() -> ProductService:
        return product_service

    def provide_order_service() -> OrderService:
        return order_service

    from litestar.di import Provide  

    # Создаём приложение с подменёнными зависимостями через Provide
    app = Litestar(
        route_handlers=[UserController, ProductController, OrderController],
        dependencies={
            "user_repository": Provide(provide_user_repository),
            "product_repository": Provide(provide_product_repository),
            "order_repository": Provide(provide_order_repository),
            "user_service": Provide(provide_user_service),
            "product_service": Provide(provide_product_service),
            "order_service": Provide(provide_order_service),
        },
    )
    return app
# ===== ФИКСТУРА: TestClient для HTTP-запросов =====
from typing import Generator

@pytest.fixture(scope="function")
def client(test_app: Litestar) -> Generator[TestClient, None, None]:
    """TestClient для тестирования API-эндпоинтов."""
    with TestClient(app=test_app) as test_client:
        yield test_client