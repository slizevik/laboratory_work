# services/product_service.py
from typing import List, Optional
from repositories.product_repository import ProductRepository
from schemas.product import ProductCreate, ProductUpdate
from models import Product

class ProductService:
    def __init__(self, product_repository: ProductRepository):
        self.product_repository = product_repository

    async def get_by_id(self, product_id: str) -> Optional[Product]:
        return await self.product_repository.get_by_id(product_id)

    async def get_all(self, count: int = 10, page: int = 1) -> List[Product]:
        return await self.product_repository.get_all(count=count, page=page)

    async def create(self, product_data: ProductCreate) -> Product:
        # Проверка: нельзя создать товар с отрицательным количеством
        if product_data.stock_quantity < 0:
            raise ValueError("Stock quantity cannot be negative")
        if product_data.price <= 0:
            raise ValueError("Price must be positive")

        return await self.product_repository.create(product_data)

    async def update(self, product_id: str, update_data: ProductUpdate) -> Optional[Product]:
        product = await self.get_by_id(product_id)
        if not product:
            return None

        # Валидация обновлений
        if update_data.stock_quantity is not None and update_data.stock_quantity < 0:
            raise ValueError("Stock quantity cannot be negative")
        if update_data.price is not None and update_data.price <= 0:
            raise ValueError("Price must be positive")

        return await self.product_repository.update(product_id, update_data)

    async def delete(self, product_id: str) -> bool:
        return await self.product_repository.delete(product_id)

    async def get_total_count(self) -> int:
        return await self.product_repository.get_total_count()