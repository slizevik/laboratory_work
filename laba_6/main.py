# main.py
import os
from contextlib import asynccontextmanager
from litestar import Litestar
from litestar.di import Provide
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import AsyncGenerator
from faststream.rabbit import RabbitBroker
import sys

# Импорты (оставляем как есть)
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

# --- Конфигурация ---
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@postgres:5432/postgres")
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://app:app@rabbitmq:5672/local")

# --- Инициализация ---
engine = create_async_engine(DATABASE_URL, echo=False)
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# --- DI провайдеры (ОСТАВЛЯЕМ КАК ЕСТЬ!) ---
async def provide_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session

async def provide_user_repository(db_session: AsyncSession = Provide(provide_db_session)) -> UserRepository:
    return UserRepository(db_session)

async def provide_product_repository(db_session: AsyncSession = Provide(provide_db_session)) -> ProductRepository:
    return ProductRepository(db_session)

async def provide_order_repository(db_session: AsyncSession = Provide(provide_db_session)) -> OrderRepository:
    return OrderRepository(db_session)

async def provide_user_service(user_repository: UserRepository = Provide(provide_user_repository)) -> UserService:
    return UserService(user_repository)

async def provide_product_service(product_repository: ProductRepository = Provide(provide_product_repository)) -> ProductService:
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

# --- Lifespan для управления брокером ---
@asynccontextmanager
async def lifespan(app: Litestar):
    """Управление жизненным циклом приложения"""
    print("Запуск брокера RabbitMQ...")
    
    # Создаем и запускаем брокер
    broker = RabbitBroker(RABBITMQ_URL)
    
    # Регистрируем обработчики RabbitMQ
    @broker.subscriber("order")
    async def handle_order(order_data: dict):
        print(f"Получен заказ: {order_data}")
        try:
            # Создаем сессию вручную (FastStream не поддерживает DI Litestar)
            async with async_session_factory() as session:
                order_repo = OrderRepository(session)
                product_repo = ProductRepository(session) 
                user_repo = UserRepository(session)
                order_service = OrderService(order_repo, product_repo, user_repo)
                # Ваша логика обработки
                print("Заказ обработан.")
        except Exception as e:
            print(f"Ошибка обработки заказа: {e}")
    
    @broker.subscriber("product")
    async def handle_product(product_data: dict):
        print(f"Получена продукция: {product_data}")
        try:
            async with async_session_factory() as session:
                product_repo = ProductRepository(session)
                product_service = ProductService(product_repo)
                # Ваша логика обработки
                print("Продукция обработана.")
        except Exception as e:
            print(f"Ошибка обработки продукции: {e}")
    
    # Запускаем брокер
    await broker.start()
    print("Брокер RabbitMQ запущен")
    
    # Сохраняем брокер в состоянии приложения
    app.state.broker = broker
    
    yield
    
    # Останавливаем брокер при завершении
    print("Остановка брокера RabbitMQ...")
    await broker.close()
    print("Брокер RabbitMQ остановлен")
    
    # Закрываем соединения с БД
    await engine.dispose()
    print("Соединения с БД закрыты")

# --- Создание приложения Litestar ---
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
    lifespan=[lifespan],
)
if __name__ == "__main__":
    import uvicorn
    print("Запуск сервера с FastStream и Litestar на http://0.0.0.0:8000")
    uvicorn.run(
        app,
        host="0.0.0.0", 
        port=8000, 
        lifespan="on",
        reload=False,
        log_level="info"
    )