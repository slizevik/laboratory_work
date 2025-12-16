# services/order_service.py
from typing import List, Optional
from repositories.order_repository import OrderRepository
from repositories.product_repository import ProductRepository
from repositories.user_repository import UserRepository
from schemas.order import OrderCreate
from models import Order


class OrderService:
    def __init__(
        self,
        order_repository: OrderRepository,
        product_repository: ProductRepository,
        user_repository: UserRepository,
    ):
        self.order_repository = order_repository
        self.product_repository = product_repository
        self.user_repository = user_repository

    async def get_by_id(self, order_id: str) -> Optional[Order]:
        return await self.order_repository.get_by_id(order_id)

    async def get_all(self, count: int = 10, page: int = 1) -> List[Order]:
        return await self.order_repository.get_all(count, page)

    async def create(self, order_data: OrderCreate) -> Order:
        # Проверка: существует ли пользователь
        user = await self.user_repository.get_by_id(order_data.user_id)
        if not user:
            raise ValueError(f"User with ID {order_data.user_id} not found")

        # Проверка: все ли продукты существуют и достаточно ли их на складе
        for product_id in order_data.product_ids:
            product = await self.product_repository.get_by_id(product_id)
            if not product:
                raise ValueError(f"Product with ID {product_id} not found")
            if product.stock_quantity < 1:
                raise ValueError(f"Product '{product.name}' is out of stock")

        # Создаём заказ (в репозитории уже снижаются остатки)
        return await self.order_repository.create(order_data)

    async def update_status(self, order_id: str, new_status: str) -> Optional[Order]:
        order = await self.get_by_id(order_id)
        if not order:
            return None

        return await self.order_repository.update(order_id, new_status)

    async def delete(self, order_id: str) -> bool:
        return await self.order_repository.delete(order_id)

    async def get_total_count(self) -> int:
        return await self.order_repository.get_total_count()