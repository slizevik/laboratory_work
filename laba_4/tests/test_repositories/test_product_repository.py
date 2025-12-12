# tests/test_repositories/test_product_repository.py
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Product
from repositories.product_repository import ProductRepository
from schemas.product import ProductCreate, ProductUpdate


@pytest.mark.asyncio
async def test_create_product(product_repository: ProductRepository, test_db_session: AsyncSession):
    """Тестирует создание продукта."""
    product_data = ProductCreate(
        name="Test Product",
        description="A product for testing",
        price=100.0,
        stock_quantity=10
    )
    product = await product_repository.create(product_data)

    assert product.name == "Test Product"
    assert product.stock_quantity == 10

    # Проверим, что продукт сохранился в БД
    result = await test_db_session.execute(select(Product).where(Product.id == product.id))
    saved_product = result.scalar_one_or_none()
    assert saved_product is not None
    assert saved_product.name == "Test Product"


@pytest.mark.asyncio
async def test_get_product_by_id(product_repository: ProductRepository, test_db_session: AsyncSession):
    """Тестирует получение продукта по ID."""
    product_data = ProductCreate(
        name="Test Product",
        description="A product for testing",
        price=100.0,
        stock_quantity=10
    )
    created_product = await product_repository.create(product_data)
    await test_db_session.commit()

    product = await product_repository.get_by_id(created_product.id)

    assert product is not None
    assert product.name == "Test Product"


@pytest.mark.asyncio
async def test_update_product(product_repository: ProductRepository, test_db_session: AsyncSession):
    """Тестирует обновление продукта."""
    product_data = ProductCreate(
        name="Original Product",
        description="Original description",
        price=100.0,
        stock_quantity=10
    )
    created_product = await product_repository.create(product_data)
    await test_db_session.commit()

    update_data = ProductUpdate(name="Updated Product", price=150.0)
    updated_product = await product_repository.update(created_product.id, update_data)

    assert updated_product is not None
    assert updated_product.name == "Updated Product"
    assert updated_product.price == 150.0
    assert updated_product.stock_quantity == 10  # не изменён


@pytest.mark.asyncio
async def test_delete_product(product_repository: ProductRepository, test_db_session: AsyncSession):
    """Тестирует удаление продукта."""
    product_data = ProductCreate(
        name="To Delete",
        description="A product for deletion",
        price=100.0,
        stock_quantity=5
    )
    created_product = await product_repository.create(product_data)
    await test_db_session.commit()

    result = await product_repository.delete(created_product.id)

    assert result is True

    # Проверим, что продукта больше нет в БД
    result = await test_db_session.execute(select(Product).where(Product.id == created_product.id))
    deleted_product = result.scalar_one_or_none()
    assert deleted_product is None


@pytest.mark.asyncio
async def test_get_all_products(product_repository: ProductRepository, test_db_session: AsyncSession):
    """Тестирует получение списка продуктов."""
    products_data = [
        ProductCreate(
            name="Product 1",
            description="Description 1",
            price=100.0,
            stock_quantity=5
        ),
        ProductCreate(
            name="Product 2",
            description="Description 2",
            price=200.0,
            stock_quantity=10
        ),
    ]
    for data in products_data:
        await product_repository.create(data)
    await test_db_session.commit()

    products = await product_repository.get_all(count=10, page=1)

    assert len(products) == 2
    assert products[0].name == "Product 1"
    assert products[1].name == "Product 2"