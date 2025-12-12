# init_db.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import Base, User, Address, Product, Order, order_product
import uuid

# Подключение к PostgreSQL (Docker Toolbox)
DATABASE_URL = "postgresql://postgres:postgres@192.168.99.100:5432/postgres"
engine = create_engine(DATABASE_URL, echo=False)

#  Сначала УДАЛЯЕМ все таблицы
print("Удаляем все существующие таблицы...")
Base.metadata.drop_all(engine)

# Затем создаём их заново (теперь как VARCHAR(36))
print("Создаём таблицы заново...")
Base.metadata.create_all(engine)

# Создаём сессию
session_factory = sessionmaker(bind=engine)

with session_factory() as session:
    print("Таблицы пересозданы. Заполняем данными...")

    # === ПОЛЬЗОВАТЕЛИ ===
    users_data = [
        {"username": "John Doe", "email": "jdoe@example.com"},
        {"username": "Jane Smith", "email": "jane@example.com"},
        {"username": "Bob Johnson", "email": "bob@example.com"},
        {"username": "Alice Brown", "email": "alice@example.com"},
        {"username": "Charlie Wilson", "email": "charlie@example.com"}
    ]
    users = [User(**u) for u in users_data]
    session.add_all(users)
    session.commit()

    # === АДРЕСА ===
  
    addresses = []
    for i, addr in enumerate([
        {"street": "123 Main St", "city": "New York", "country": "USA"},
        {"street": "456 Oak Ave", "city": "Los Angeles", "country": "USA"},
        {"street": "789 Pine Rd", "city": "Chicago", "country": "USA"},
        {"street": "321 Elm St", "city": "Miami", "country": "USA"},
        {"street": "654 Maple Dr", "city": "Seattle", "country": "USA"}
    ]):
        address = Address(
            user_id=users[i].id,
            street=addr["street"],
            city=addr["city"],
            state="",          
            zip_code="",       
            country=addr["country"],
            is_primary=True
        )
        addresses.append(address)

    session.add_all(addresses)
    session.commit()
    # === ПРОДУКТЫ ===
    products_data = [
        {"name": "Ноутбук", "description": "Мощный игровой ноутбук", "price": 85000.0, "stock_quantity": 10},
        {"name": "Мышь", "description": "Беспроводная игровая мышь", "price": 2500.0, "stock_quantity": 50},
        {"name": "Клавиатура", "description": "Механическая клавиатура", "price": 6000.0, "stock_quantity": 20}
    ]
    products = [Product(**p) for p in products_data]
    session.add_all(products)
    session.commit()

    # === ЗАКАЗЫ ===
    order1 = Order(user_id=users[0].id, status="completed")
    order2 = Order(user_id=users[1].id, status="pending")
    session.add_all([order1, order2])
    session.flush()

    from sqlalchemy import insert
    session.execute(
        insert(order_product),
        [
            {"order_id": order1.id, "product_id": products[0].id, "quantity": 1},
            {"order_id": order1.id, "product_id": products[1].id, "quantity": 1},
            {"order_id": order2.id, "product_id": products[2].id, "quantity": 2},
        ]
    )
    session.commit()

    print("База данных полностью инициализирована!")