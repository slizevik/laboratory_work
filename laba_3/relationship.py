from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, selectinload
from models import User, Address

# Подключение к PostgreSQL
engine = create_engine(
    "postgresql://postgres:postgres@192.168.99.100:5432/postgres",
    echo=True
)

session_factory = sessionmaker(bind=engine)

print("\n" + "=" * 50)
print("ПОЛУЧАЕМ ПОЛЬЗОВАТЕЛЕЙ С ИХ АДРЕСАМИ")
print("=" * 50)

with session_factory() as session:
    # Получаем всех пользователей с их адресами
    stmt = select(User).options(selectinload(User.addresses))
    users_with_addresses = session.execute(stmt).scalars().all()

    for user in users_with_addresses:
        print(f"\nПользователь: {user.username} ({user.email})")
        print("Адреса:")
        for address in user.addresses:
            print(f"  - {address.street}, {address.city}, {address.country}")


print("ПОЛУЧАЕМ АДРЕСА С ИНФОРМАЦИЕЙ О ПОЛЬЗОВАТЕЛЯХ")


with session_factory() as session:
    # Получаем все адреса с информацией о пользователях
    stmt = select(Address).options(selectinload(Address.user))
    addresses_with_users = session.execute(stmt).scalars().all()

    for address in addresses_with_users:
        print(f"\nАдрес: {address.street}, {address.city}")
        print(f"Пользователь: {address.user.username} ({address.user.email})")