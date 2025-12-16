# seed_data.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import Product, Order, order_product, Base
import uuid
import os

# Подключение к БД (тот же URL, что в main.py, но в синхронном формате)
ASYNC_DATABASE_URL_DEFAULT = "postgresql+asyncpg://postgres:postgres@postgres:5432/postgres"
ASYNC_DATABASE_URL = os.getenv("DATABASE_URL", ASYNC_DATABASE_URL_DEFAULT)
DATABASE_URL = ASYNC_DATABASE_URL.replace("+asyncpg", "")

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

def main():
    session = SessionLocal()
    try:
        print("Очищаем таблицы: order_product, orders, products...")
        session.execute(text("DELETE FROM order_product"))
        session.execute(text("DELETE FROM orders"))
        session.execute(text("DELETE FROM products"))
        session.commit()
        print(" Таблицы очищены")

        print("Добавляем 3 продукта...")
        products = [
            Product(name="Ноутбук", description="Мощный игровой ноутбук", price=85000.0, stock_quantity=10),
            Product(name="Мышь", description="Беспроводная игровая мышь", price=2500.0, stock_quantity=50),
            Product(name="Клавиатура", description="Механическая клавиатура", price=6000.0, stock_quantity=20),
        ]
        session.add_all(products)
        session.commit()
        print(" Продукты добавлены")

        print("Получаем ID пользователей (уже существуют)...")
        result = session.execute(text("SELECT id FROM users LIMIT 2"))
        user_ids = [row[0] for row in result.fetchall()]
        if len(user_ids) < 2:
            raise Exception("Нужно сначала запустить init_db.py (должно быть минимум 2 пользователя)")

        # Создаём заказы
        order1 = Order(user_id=user_ids[0], status="completed")
        order2 = Order(user_id=user_ids[1], status="pending")
        session.add_all([order1, order2])
        session.flush()  # Получаем ID заказов

        # Связываем с продуктами
        session.execute(
            order_product.insert(),
            [
                {"order_id": order1.id, "product_id": products[0].id, "quantity": 1},
                {"order_id": order1.id, "product_id": products[1].id, "quantity": 1},
                {"order_id": order2.id, "product_id": products[2].id, "quantity": 2},
            ]
        )
        session.commit()
        print(" Заказы созданы!")

    except Exception as e:
        session.rollback()
        print(f"Ошибка: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    main()