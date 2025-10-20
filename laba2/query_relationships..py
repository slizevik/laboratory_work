from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, selectinload
from models import User, Address


engine = create_engine(
    "postgresql://postgres:postgres@192.168.99.100:5432/postgres",
    echo=True
)

session_factory = sessionmaker(bind=engine)

print("ЗАПРОС СВЯЗАННЫХ ДАННЫХ ")
print("Демонстрация связи между таблицами users и addresses")

with session_factory() as session:

    print("\n1. SELECT с selectinload:")
    query = select(User).options(selectinload(User.addresses))
    users_with_addresses = session.execute(query).scalars().all()

    for user in users_with_addresses:
        print(f"\nПользователь: {user.username} ({user.email}):")
        if user.addresses:
            for address in user.addresses:
                print(f"   Адрес: {address.street}, {address.city}, {address.country}")
        else:
            print("   Нет адресов")


    print("\n" + "=" * 50)
    print("2. ОБРАТНАЯ СВЯЗЬ: АДРЕС - ПОЛЬЗОВАТЕЛЬ")

    addresses_query = select(Address).options(selectinload(Address.user))
    addresses_with_users = session.execute(addresses_query).scalars().all()

    for address in addresses_with_users:
        print(f"\nАдрес: {address.street}, {address.city}")
        print(f"   Владелец: {address.user.username} ({address.user.email})")


    print("\n" + "=" * 50)
    print("3. СТАТИСТИКА:")
    user_count = session.query(User).count()
    address_count = session.query(Address).count()

    print(f"   Всего пользователей: {user_count}")
    print(f"   Всего адресов: {address_count}")
    print(f"   Связь: Один пользователь -> Много адресов")

print("\nЗапросы связанных данных выполнены успешно!")