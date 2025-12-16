# tests/test_conftest.py
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_database_connection(test_db_session: AsyncSession):
    """Проверяем подключение к in-memory SQLite."""
    result = await test_db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1

@pytest.mark.asyncio
async def test_user_repository_fixture(user_repository):
    """Проверяем, что фикстура репозитория пользователя работает."""
    assert user_repository is not None

@pytest.mark.asyncio
async def test_user_service_fixture(user_service):
    """Проверяем, что фикстура сервиса пользователя работает."""
    assert user_service is not None

@pytest.mark.asyncio
async def test_litestar_app_fixture(test_app):
    """Проверяем, что тестовое приложение создаётся."""
    assert test_app is not None

@pytest.mark.asyncio
async def test_testclient_fixture(client):
    """Проверяем, что TestClient создаётся."""
    assert client is not None