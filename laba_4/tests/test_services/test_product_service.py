# tests/test_services/test_product_service.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from models import Product
from repositories.product_repository import ProductRepository
from services.product_service import ProductService
from schemas.product import ProductCreate, ProductUpdate


@pytest.mark.asyncio
async def test_product_service_create():
    """Тестирует создание продукта через ProductService с mock-репозиторием."""
    # Создаём mock-репозитория
    mock_repo = AsyncMock(spec=ProductRepository)
    product_service = ProductService(mock_repo)

    # Подготовим данные
    product_data = ProductCreate(
        name="Test Product",
        description="A product for testing",
        price=100.0,
        stock_quantity=10
    )
    # Подменяем create, чтобы он возвращал mock-объект
    mock_product = Product(
        id="123",
        name="Test Product",
        description="A product for testing",
        price=100.0,
        stock_quantity=10
    )
    mock_repo.create.return_value = mock_product  

    # Вызываем метод сервиса
    result = await product_service.create(product_data)

    mock_repo.create.assert_called_once_with(product_data)  
    # Проверяем результат
    assert result.name == "Test Product"


@pytest.mark.asyncio
async def test_product_service_get_by_id():
    """Тестирует получение продукта по ID."""
    mock_repo = AsyncMock(spec=ProductRepository)
    product_service = ProductService(mock_repo)

    mock_product = Product(
        id="123",
        name="Test Product",
        description="A product for testing",
        price=100.0,
        stock_quantity=10
    )
    mock_repo.get_by_id.return_value = mock_product

    result = await product_service.get_by_id("123")

    mock_repo.get_by_id.assert_called_once_with("123")  
    assert result.id == "123"


@pytest.mark.asyncio
async def test_product_service_get_by_id_not_found():
    """Тестирует получение несуществующего продукта."""
    mock_repo = AsyncMock(spec=ProductRepository)
    product_service = ProductService(mock_repo)

    mock_repo.get_by_id.return_value = None

    result = await product_service.get_by_id("nonexistent")

    mock_repo.get_by_id.assert_called_once_with("nonexistent")  
    assert result is None


@pytest.mark.asyncio
async def test_product_service_update():
    """Тестирует обновление продукта."""
    mock_repo = AsyncMock(spec=ProductRepository)
    product_service = ProductService(mock_repo)

    existing_product = Product(
        id="123",
        name="Old Name",
        description="Old Description",
        price=100.0,
        stock_quantity=10
    )
    mock_repo.get_by_id.return_value = existing_product

    update_data = ProductUpdate(name="New Name", price=150.0)
    updated_product = Product(
        id="123",
        name="New Name",
        description="Old Description",
        price=150.0,
        stock_quantity=10
    )
    mock_repo.update.return_value = updated_product

    result = await product_service.update("123", update_data)

    mock_repo.update.assert_called_once_with("123", update_data)  
    assert result.name == "New Name"
    assert result.price == 150.0


@pytest.mark.asyncio
async def test_product_service_delete():
    """Тестирует удаление продукта."""
    mock_repo = AsyncMock(spec=ProductRepository)
    product_service = ProductService(mock_repo)

    mock_repo.delete.return_value = True

    result = await product_service.delete("123")

    mock_repo.delete.assert_called_once_with("123")  
    assert result is True