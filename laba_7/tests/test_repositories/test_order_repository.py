# tests/test_repositories/test_order_repository.py
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Order, Product, order_product
from repositories.order_repository import OrderRepository
from repositories.product_repository import ProductRepository
from repositories.user_repository import UserRepository
from schemas.order import OrderCreate
from schemas.user import UserCreate
from schemas.product import ProductCreate


@pytest.mark.asyncio
async def test_create_order_with_products(
    order_repository: OrderRepository,
    product_repository: ProductRepository,
    user_repository: UserRepository,
    test_db_session: AsyncSession
):
    """Тестирует создание заказа с несколькими продуктами."""
    # Создаём пользователя
    user_data = UserCreate(username="Test User", email="test@example.com")
    user = await user_repository.create(user_data)
    await test_db_session.commit()

    # Создаём продукты
    product1_data = ProductCreate(name="Product 1", price=100.0, stock_quantity=5)
    product2_data = ProductCreate(name="Product 2", price=200.0, stock_quantity=10)
    product1 = await product_repository.create(product1_data)
    product2 = await product_repository.create(product2_data)
    await test_db_session.commit()

    # Подготовим данные для создания заказа
    order_data = OrderCreate(user_id=user.id, product_ids=[product1.id, product2.id])

    order = await order_repository.create(order_data)

    assert order.user_id == user.id
    assert order.status == "pending"

    # Проверим, что заказ сохранился в БД
    result = await test_db_session.execute(select(Order).where(Order.id == order.id))
    saved_order = result.scalar_one_or_none()
    assert saved_order is not None

    # Проверим, что продукты связаны с заказом
    result = await test_db_session.execute(
        select(order_product).where(order_product.c.order_id == order.id)
    )
    links = result.fetchall()
    assert len(links) == 2
    assert {link.product_id for link in links} == {product1.id, product2.id}


@pytest.mark.asyncio
async def test_get_order_by_id(
    order_repository: OrderRepository,
    product_repository: ProductRepository,
    user_repository: UserRepository,
    test_db_session: AsyncSession
):
    """Тестирует получение заказа по ID."""
    # Создаём пользователя и продукты
    user_data = UserCreate(username="Test User", email="test@example.com")
    user = await user_repository.create(user_data)
    product_data = ProductCreate(name="Test Product", price=100.0, stock_quantity=5)
    product = await product_repository.create(product_data)
    await test_db_session.commit()

    # Создаём заказ
    order_data = OrderCreate(user_id=user.id, product_ids=[product.id])
    created_order = await order_repository.create(order_data)
    await test_db_session.commit()

    order = await order_repository.get_by_id(created_order.id)

    assert order is not None
    assert order.user_id == user.id
    assert len(order.products) == 1
    assert order.products[0].id == product.id


@pytest.mark.asyncio
async def test_update_order_status(order_repository: OrderRepository, test_db_session: AsyncSession):
    """Тестирует обновление статуса заказа."""
    # Пока пропущен
    pass


@pytest.mark.asyncio
async def test_delete_order(order_repository: OrderRepository, test_db_session: AsyncSession):
    """Тестирует удаление заказа."""
    # Пока пропущен
    pass


@pytest.mark.asyncio
async def test_get_all_orders(
    order_repository: OrderRepository,
    product_repository: ProductRepository,
    user_repository: UserRepository,
    test_db_session: AsyncSession
):
    """Тестирует получение списка заказов."""
    # Создаём пользователя и продукты
    user_data = UserCreate(username="Test User", email="test@example.com")
    user = await user_repository.create(user_data)
    product_data = ProductCreate(name="Test Product", price=100.0, stock_quantity=5)
    product = await product_repository.create(product_data)
    await test_db_session.commit()

    # Создаём два заказа
    order_data1 = OrderCreate(user_id=user.id, product_ids=[product.id])
    order_data2 = OrderCreate(user_id=user.id, product_ids=[product.id])
    await order_repository.create(order_data1)
    await order_repository.create(order_data2)
    await test_db_session.commit()

    orders = await order_repository.get_all(count=10, page=1)

    assert len(orders) == 2