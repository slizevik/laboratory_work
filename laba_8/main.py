# main.py
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
import sys
import os

from litestar import Litestar
from litestar.di import Provide
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from faststream.rabbit import RabbitBroker
from redis.asyncio import Redis

# Импорты (оставляем как есть)
from models import User, Product, Order
from controllers.user_controller import UserController
from controllers.product_controller import ProductController
from controllers.order_controller import OrderController
from controllers.report_controller import ReportController
from repositories.user_repository import UserRepository
from repositories.product_repository import ProductRepository
from repositories.order_repository import OrderRepository
from repositories.report_repository import ReportRepository
from services.user_service import UserService
from services.product_service import ProductService
from services.order_service import OrderService
from services.report_service import ReportService

# --- Конфигурация ---
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@postgres:5432/postgres")
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://app:app@rabbitmq:5672/local")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

# --- Инициализация ---
engine = create_async_engine(DATABASE_URL, echo=False)
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
redis_client: Optional[Redis] = None


# --- Redis провайдер ---
async def provide_redis_client() -> Redis:
    if not redis_client:
        raise RuntimeError("Redis client is not initialized")
    return redis_client


async def provide_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session


async def provide_user_repository(db_session: AsyncSession) -> UserRepository:
    return UserRepository(db_session)

async def provide_product_repository(db_session: AsyncSession) -> ProductRepository:
    return ProductRepository(db_session)

async def provide_order_repository(db_session: AsyncSession) -> OrderRepository:
    return OrderRepository(db_session)

async def provide_report_repository(db_session: AsyncSession) -> ReportRepository:
    return ReportRepository(db_session)

async def provide_user_service(
    user_repository: UserRepository,
    redis_client: Redis,
) -> UserService:
    return UserService(user_repository, redis_client=redis_client)

async def provide_product_service(
    product_repository: ProductRepository,
    redis_client: Redis,
) -> ProductService:
    return ProductService(product_repository, redis_client=redis_client)

async def provide_order_service(
    order_repository: OrderRepository,
    product_repository: ProductRepository,
    user_repository: UserRepository,
) -> OrderService:
    return OrderService(
        order_repository=order_repository,
        product_repository=product_repository,
        user_repository=user_repository
    )

async def provide_report_service(
    report_repository: ReportRepository,
) -> ReportService:
    return ReportService(report_repository)


# --- Lifespan для управления брокером ---
@asynccontextmanager
async def lifespan(app: Litestar):
    """Управление жизненным циклом приложения"""
    print("Запуск брокера RabbitMQ...")
    global redis_client

    # Инициализируем Redis (один экземпляр на приложение)
    redis_client = Redis.from_url(REDIS_URL, decode_responses=True)

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
    app.state.redis = redis_client

    yield
    
    # Останавливаем брокер при завершении
    print("Остановка брокера RabbitMQ...")
    await broker.close()
    print("Брокер RabbitMQ остановлен")

    # Закрываем соединение с Redis
    if redis_client:
        await redis_client.close()
        print("Соединение с Redis закрыто")

    # Закрываем соединения с БД
    await engine.dispose()
    print("Соединения с БД закрыты")

# --- Создание приложения Litestar ---
app = Litestar(
    route_handlers=[UserController, ProductController, OrderController, ReportController],
    dependencies={
        "db_session": provide_db_session,
        "user_repository": provide_user_repository,
        "product_repository": provide_product_repository,
        "order_repository": provide_order_repository,
        "report_repository": provide_report_repository,
        "user_service": provide_user_service,
        "product_service": provide_product_service,
        "order_service": provide_order_service,
        "report_service": provide_report_service,
        "redis_client": provide_redis_client,
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