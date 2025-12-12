# main.py
import os
from litestar import Litestar
from litestar.di import Provide
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import AsyncGenerator

from models import User, Product, Order
from controllers.user_controller import UserController
from controllers.product_controller import ProductController
from controllers.order_controller import OrderController
from repositories.user_repository import UserRepository
from repositories.product_repository import ProductRepository
from repositories.order_repository import OrderRepository
from services.user_service import UserService
from services.product_service import ProductService
from services.order_service import OrderService

# Для Docker Toolbox: 192.168.99.100 — правильный адрес
DATABASE_URL = "postgresql+asyncpg://postgres:postgres@192.168.99.100:5432/postgres"

engine = create_async_engine(DATABASE_URL, echo=False)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def provide_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session

async def provide_user_repository(
    db_session: AsyncSession = Provide(provide_db_session)
) -> UserRepository:
    return UserRepository(db_session)

async def provide_product_repository(
    db_session: AsyncSession = Provide(provide_db_session)
) -> ProductRepository:
    return ProductRepository(db_session)

async def provide_order_repository(
    db_session: AsyncSession = Provide(provide_db_session)
) -> OrderRepository:
    return OrderRepository(db_session)

async def provide_user_service(
    user_repository: UserRepository = Provide(provide_user_repository)
) -> UserService:
    return UserService(user_repository)

async def provide_product_service(
    product_repository: ProductRepository = Provide(provide_product_repository)
) -> ProductService:
    return ProductService(product_repository)

async def provide_order_service(
    order_repository: OrderRepository = Provide(provide_order_repository),
    product_repository: ProductRepository = Provide(provide_product_repository),
    user_repository: UserRepository = Provide(provide_user_repository),
) -> OrderService:
    return OrderService(
        order_repository=order_repository,
        product_repository=product_repository,
        user_repository=user_repository
    )

app = Litestar(
    route_handlers=[UserController, ProductController, OrderController],
    dependencies={
        "db_session": Provide(provide_db_session),
        "user_repository": Provide(provide_user_repository),
        "product_repository": Provide(provide_product_repository),
        "order_repository": Provide(provide_order_repository),
        "user_service": Provide(provide_user_service),
        "product_service": Provide(provide_product_service),
        "order_service": Provide(provide_order_service),
    },
)

if __name__ == "__main__":
    import uvicorn
    print("Запуск сервера на http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)