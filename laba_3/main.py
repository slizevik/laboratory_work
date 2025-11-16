from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User, Address, Base

# Подключение к PostgreSQL
engine = create_engine(
    "postgresql://postgres:postgres@192.168.99.100:5432/postgres",
    echo=True
)

# Создаем таблицы
Base.metadata.create_all(engine)

session_factory = sessionmaker(bind=engine)

with session_factory() as session:
    print("СОЗДАЕМ 5 ПОЛЬЗОВАТЕЛЕЙ И АДРЕСОВ")

    # Создаем 5 пользователей
    users_data = [
        {"username": "John Doe", "email": "jdoe@example.com"},
        {"username": "Jane Smith", "email": "jane@example.com"},
        {"username": "Bob Johnson", "email": "bob@example.com"},
        {"username": "Alice Brown", "email": "alice@example.com"},
        {"username": "Charlie Wilson", "email": "charlie@example.com"}
    ]

    users = []
    for user_data in users_data:
        user = User(username=user_data["username"], email=user_data["email"])
        users.append(user)
        session.add(user)
        print(f"Создан пользователь: {user.username}")

    session.commit()
    print("5 пользователей создано!")

    # Создаем адреса для каждого пользователя
    addresses_data = [
        {"street": "123 Main St", "city": "New York", "country": "USA"},
        {"street": "456 Oak Ave", "city": "Los Angeles", "country": "USA"},
        {"street": "789 Pine Rd", "city": "Chicago", "country": "USA"},
        {"street": "321 Elm St", "city": "Miami", "country": "USA"},
        {"street": "654 Maple Dr", "city": "Seattle", "country": "USA"}
    ]

    for i, address_data in enumerate(addresses_data):
        address = Address(
            user_id=users[i].id,
            street=address_data["street"],
            city=address_data["city"],
            state="",
            zip_code="",
            country=address_data["country"],
            is_primary=True
        )
        session.add(address)
        print(f"Создан адрес для {users[i].username}: {address_data['street']}")

    session.commit()
    print("5 адресов создано")
    print("База данных полностью заполнена")
