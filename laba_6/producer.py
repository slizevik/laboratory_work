import asyncio
import json
import os
import random
from aio_pika import connect_robust, Message, ExchangeType


RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://app:app@rabbitmq:5672/local")


async def main():
    # Подключение к RabbitMQ
    # URL берём из переменной окружения, как и в main.py (в Docker это app:app@rabbitmq:5672/local)
    connection = await connect_robust(RABBITMQ_URL)
    # Открываем канал
    channel = await connection.channel()

    # Получаем ссылку на default exchange (очереди уже созданы приложением app)
    exchange = channel.default_exchange

    # --- Отправляем 5 сообщений о продукции ---
    print("Отправка 5 сообщений о продукции...")
    for i in range(1, 6):
        product_data = {
            "id": i,
            "name": f"Product {i}",
            "price": round(random.uniform(10.0, 100.0), 2),
            "quantity": random.randint(1, 100)
        }
        message = Message(
            json.dumps(product_data).encode('utf-8'),
            delivery_mode=2,  # Делаем сообщение устойчивым (persistent)
        )
        await exchange.publish(
            message,
            routing_key='product',  # Отправляем в очередь 'product'
        )
        print(f"  Отправлено: {product_data}")

    # --- Отправляем 3 сообщения о заказах ---
    print("\nОтправка 3 сообщений о заказах...")
    for i in range(1, 4):
        # Создаем список позиций заказа (items)
        # Пусть каждый заказ содержит 1-3 случайных продукта
        num_items = random.randint(1, 3)
        items = []
        for _ in range(num_items):
            item_product_id = random.randint(1, 5) # Выбираем продукт из отправленных выше
            item_quantity = random.randint(1, min(5, 10)) # Количество не больше 5 и не больше, чем в заказе
            items.append({
                "product_id": item_product_id,
                "quantity": item_quantity
            })

        order_data = {
            "id": i,
            "user_id": random.randint(1, 10), # Случайный user_id
            "items": items,
            "status": "pending" # Новый заказ
        }
        message = Message(
            json.dumps(order_data).encode('utf-8'),
            delivery_mode=2,  # Делаем сообщение устойчивым (persistent)
        )
        await exchange.publish(
            message,
            routing_key='order',  # Отправляем в очередь 'order'
        )
        print(f"  Отправлено: {order_data}")

    print("\nВсе сообщения отправлены.")

    # Закрываем соединение
    await connection.close()

if __name__ == "__main__":
    asyncio.run(main())