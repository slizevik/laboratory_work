# services/product_service.py
import json
from typing import List, Optional
from redis.asyncio import Redis

from repositories.product_repository import ProductRepository
from schemas.product import ProductCreate, ProductUpdate, ProductResponse
from models import Product


PRODUCT_CACHE_TTL_SECONDS = 600  # 10 минут
PRODUCT_CACHE_KEY_PREFIX = "cache:product:"

class ProductService:
    def __init__(self, product_repository: ProductRepository, redis_client: Redis):
        self.product_repository = product_repository
        self.redis = redis_client

    async def get_by_id(self, product_id: str) -> Optional[Product]:
        cache_key = f"{PRODUCT_CACHE_KEY_PREFIX}{product_id}"

        # 1) Проверяем кэш
        cached = await self.redis.get(cache_key)
        if cached:
            data = json.loads(cached)
            return ProductResponse(**data)

        # 2) Иначе читаем из БД и кладем в кэш
        product = await self.product_repository.get_by_id(product_id)
        if product:
            payload = ProductResponse.model_validate(product).model_dump()
            await self.redis.set(cache_key, json.dumps(payload), ex=PRODUCT_CACHE_TTL_SECONDS)
        return product

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

        updated = await self.product_repository.update(product_id, update_data)

        # После обновления — обновляем кэш свежими данными
        cache_key = f"{PRODUCT_CACHE_KEY_PREFIX}{product_id}"
        if updated:
            payload = ProductResponse.model_validate(updated).model_dump()
            await self.redis.set(cache_key, json.dumps(payload), ex=PRODUCT_CACHE_TTL_SECONDS)
        else:
            await self.redis.delete(cache_key)

        return updated

    async def delete(self, product_id: str) -> bool:
        deleted = await self.product_repository.delete(product_id)
        if deleted:
            cache_key = f"{PRODUCT_CACHE_KEY_PREFIX}{product_id}"
            await self.redis.delete(cache_key)
        return deleted

    async def get_total_count(self) -> int:
        return await self.product_repository.get_total_count()