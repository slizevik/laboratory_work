import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text


async def debug_database():
    # Текущие настройки из web_app.py
    DATABASE_URL = "postgresql+asyncpg://postgres:postgres@192.168.99.100:5432/postgres"

    print("=== ДЕБАГ ПОДКЛЮЧЕНИЯ К БАЗЕ ===")
    print(f"URL: {DATABASE_URL}")

    engine = create_async_engine(DATABASE_URL, echo=True)

    try:
        async with engine.connect() as conn:
            print("✅ Подключение к БД успешно!")

            # 1. Проверим какие базы есть
            print("\n=== СПИСОК БАЗ ДАННЫХ ===")
            result = await conn.execute(text("SELECT datname FROM pg_database WHERE datistemplate = false;"))
            databases = result.scalars().all()
            for db in databases:
                print(f"   - {db}")

            # 2. Проверим какие таблицы в текущей БД
            print("\n=== ТАБЛИЦЫ В БАЗЕ 'postgres' ===")
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            tables = result.scalars().all()
            for table in tables:
                print(f"   - {table}")

            # 3. Проверим содержимое таблицы users
            if 'users' in tables:
                print("\n=== ДАННЫЕ В ТАБЛИЦЕ users ===")
                result = await conn.execute(text("SELECT COUNT(*) as count FROM users"))
                count = result.scalar()
                print(f"   Записей в users: {count}")

                if count > 0:
                    result = await conn.execute(text("SELECT id, username, email FROM users LIMIT 5"))
                    for row in result:
                        print(f"   - ID: {row[0]}, Username: {row[1]}, Email: {row[2]}")
            else:
                print("   ❌ Таблица 'users' не найдена!")

    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")


if __name__ == "__main__":
    asyncio.run(debug_database())