from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User, Address

# Подключение к БД
engine = create_engine(
    "postgresql://postgres:postgres@192.168.99.100:5432/postgres",
    echo=True
)

Session = sessionmaker(bind=engine)

with Session() as session:
    print("=== ОЧИСТКА БАЗЫ ДАННЫХ ===")

    # Удаляем все адреса
    session.query(Address).delete()
    print("✅ Все адреса удалены")

    # Удаляем всех пользователей
    session.query(User).delete()
    print("✅ Все пользователи удалены")

    session.commit()
    print("🎉 База данных полностью очищена!")

    # Проверяем что таблицы пустые
    user_count = session.query(User).count()
    address_count = session.query(Address).count()

    print(f"📊 Пользователей в БД: {user_count}")
    print(f"📊 Адресов в БД: {address_count}")
