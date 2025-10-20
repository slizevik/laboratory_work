from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User, Address, Product, Order

engine = create_engine(
    "postgresql://postgres:postgres@192.168.99.100:5432/postgres",
    echo=True
)

Session = sessionmaker(bind=engine)

print("=== ДОБАВЛЯЕМ ПРОДУКТЫ И ЗАКАЗЫ ===")

with Session() as session:
    # 1. Добавляем описание существующим пользователям
    print("1. ОБНОВЛЯЕМ ОПИСАНИЯ ПОЛЬЗОВАТЕЛЕЙ:")
    users = session.query(User).all()
    descriptions = [
        "Постоянный клиент",
        "Новый пользователь",
        "VIP клиент",
        "Корпоративный аккаунт",
        "Тестовый пользователь"
    ]

    for i, user in enumerate(users):
        user.description = descriptions[i]
        print(f"   Обновлен: {user.username}: {user.description}")

    # 2. Создаем 5 продуктов
    print("\n2. СОЗДАЕМ 5 ПРОДУКТОВ:")
    products_data = [
        {"name": "Ноутбук", "description": "Игровой ноутбук", "price": 999.99},
        {"name": "Смартфон", "description": "Флагманский смартфон", "price": 799.99},
        {"name": "Наушники", "description": "Беспроводные наушники", "price": 199.99},
        {"name": "Планшет", "description": "Графический планшет", "price": 499.99},
        {"name": "Часы", "description": "Умные часы", "price": 299.99}
    ]

    products = []
    for product_data in products_data:
        product = Product(
            name=product_data["name"],
            description=product_data["description"],
            price=product_data["price"]
        )
        products.append(product)
        session.add(product)
        print(f"   Создан: {product.name}: ${product.price}")

    # 3. Создаем 5 заказов
    print("\n3. СОЗДАЕМ 5 ЗАКАЗОВ:")

    # Получаем существующих пользователей и адреса
    users = session.query(User).all()
    addresses = session.query(Address).all()

    orders_data = [
        {"user": users[0], "address": addresses[0], "product": products[0], "quantity": 1},
        {"user": users[1], "address": addresses[1], "product": products[1], "quantity": 2},
        {"user": users[2], "address": addresses[2], "product": products[2], "quantity": 1},
        {"user": users[3], "address": addresses[3], "product": products[3], "quantity": 1},
        {"user": users[4], "address": addresses[4], "product": products[4], "quantity": 3}
    ]

    for order_data in orders_data:
        order = Order(
            user_id=order_data["user"].id,
            address_id=order_data["address"].id,
            product_id=order_data["product"].id,
            quantity=order_data["quantity"]
        )
        session.add(order)
        print(
            f"   Создан заказ: {order_data['user'].username} -> {order_data['product'].name} x{order_data['quantity']}")

    # Сохраняем все изменения
    session.commit()

    print("\nДАННЫЕ УСПЕШНО ДОБАВЛЕНЫ!")
    print(f"   Продуктов: {len(products)}")
    print(f"   Заказов: {len(orders_data)}")
    print(f"   Пользователей с описаниями: {len(users)}")