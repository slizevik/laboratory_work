# check_models.py
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from models import Base

async def check_models():
    # Используем SQLite в памяти — не трогаем твою PostgreSQL!
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("✅ Все модели корректны. Таблицы созданы успешно в SQLite (в памяти).")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_models())