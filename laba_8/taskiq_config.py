import json
import os
from datetime import datetime

import aio_pika
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from taskiq import TaskiqScheduler
from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend
from taskiq.schedule_sources import LabelScheduleSource

from models import Order, Report, order_product

"""
Базовая конфигурация TaskIQ для проекта.

Используем Redis как брокер и бэкенд результатов TaskIQ,
а также PostgreSQL для хранения отчётов и RabbitMQ для отправки кратких отчётов.
URL берём из переменных окружения, как и в main.py.
"""

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@postgres:5432/postgres",
)
RABBITMQ_URL = os.getenv(
    "RABBITMQ_URL",
    "amqp://app:app@rabbitmq:5672/local",
)

# Брокер TaskIQ на основе Redis (листовая очередь).
# Через with_result_backend подключаем хранение результатов.
broker = ListQueueBroker(url=REDIS_URL).with_result_backend(
    RedisAsyncResultBackend(redis_url=REDIS_URL),
)

# Асинхронный движок и фабрика сессий для работы с БД в задачах.
engine = create_async_engine(DATABASE_URL, echo=False)
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@broker.task
async def hello_task() -> None:
    """Простая тестовая задача для проверки работоспособности TaskIQ."""
    print("Hello from TaskIQ!")


@broker.task(
    # Запускать задачу раз в минуту.
    schedule=[
        {
            "cron": "*/1 * * * *",
            "args": [],
            "kwargs": {},
        }
    ],
)
async def my_scheduled_task() -> None:
    """Плановая задача формирования отчётов по заказам.

    - собирает данные по заказам;
    - считает количество товаров в каждом заказе;
    - сохраняет отчёты в таблицу reports;
    - отправляет краткий отчёт в очередь RabbitMQ.
    """
    print("[my_scheduled_task] Запуск задачи отчёта по заказам")

    # 1. Собираем данные по заказам и количеству товаров.
    async with async_session_factory() as session:
        # SELECT order_id, COALESCE(SUM(quantity), 0) AS count_product
        # FROM order_product LEFT JOIN orders ... GROUP BY order_id;
        stmt = (
            select(
                Order.id,
                func.coalesce(func.sum(order_product.c.quantity), 0).label(
                    "count_product",
                ),
            )
            .join(
                order_product,
                order_product.c.order_id == Order.id,
                isouter=True,
            )
            .group_by(Order.id)
        )

        result = await session.execute(stmt)
        rows = result.all()

        now = datetime.now()
        report_payload: list[dict] = []

        for order_id, count_product in rows:
            # Создаём запись отчёта в БД.
            report = Report(
                order_id=order_id,
                count_product=int(count_product or 0),
                report_at=now,
            )
            session.add(report)

            report_payload.append(
                {
                    "order_id": order_id,
                    "count_product": int(count_product or 0),
                    "report_at": now.isoformat(),
                },
            )

        await session.commit()

    print(
        f"[my_scheduled_task] Сформировано отчётов: {len(report_payload)}. "
        f"Отправляем краткий отчёт в RabbitMQ...",
    )

    # 2. Отправляем краткий отчёт в RabbitMQ.
    if not report_payload:
        print("[my_scheduled_task] Нет данных для отправки в RabbitMQ.")
        return

    try:
        connection = await aio_pika.connect_robust(RABBITMQ_URL)
        async with connection:
            channel = await connection.channel()

            # Объявляем очередь для отчётов (если её ещё нет).
            queue_name = "order_reports"
            await channel.declare_queue(queue_name, durable=True)

            message_body = json.dumps(report_payload).encode("utf-8")

            await channel.default_exchange.publish(
                aio_pika.Message(body=message_body),
                routing_key=queue_name,
            )

        print(
            f"[my_scheduled_task] Отправлено {len(report_payload)} записей в очередь '{queue_name}'.",
        )
    except Exception as exc:  # pragma: no cover - защита от сбоёв внешних сервисов
        print(f"[my_scheduled_task] Ошибка при отправке сообщения в RabbitMQ: {exc}")


# Планировщик, который будет искать задачи по лейблам/регистрации в брокере,
# в том числе my_scheduled_task (через LabelScheduleSource).
scheduler = TaskiqScheduler(
    broker=broker,
    sources=[LabelScheduleSource(broker)],
)
