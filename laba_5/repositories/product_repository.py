# repositories/product_repository.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from models import Product
from schemas.product import ProductCreate, ProductUpdate

class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, product_id: str) -> Optional[Product]:
        result = await self.session.execute(select(Product).where(Product.id == product_id))
        return result.scalar_one_or_none()

    async def get_all(self, count: int = 10, page: int = 1) -> List[Product]:
        offset = (page - 1) * count
        result = await self.session.execute(select(Product).offset(offset).limit(count))
        return result.scalars().all()

    async def create(self, product_data: ProductCreate) -> Product:
        product = Product(
            name=product_data.name,
            description=product_data.description,
            price=product_data.price,
            stock_quantity=product_data.stock_quantity
        )
        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        return product

    async def update(self, product_id: str, product_data: ProductUpdate) -> Optional[Product]:
        product = await self.get_by_id(product_id)
        if not product:
            return None

        update_data = product_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(product, field):
                setattr(product, field, value)

        await self.session.commit()
        await self.session.refresh(product)
        return product

    async def delete(self, product_id: str) -> bool:
        product = await self.get_by_id(product_id)
        if not product:
            return False
        await self.session.delete(product)
        await self.session.commit()
        return True

    async def get_total_count(self) -> int:
        result = await self.session.execute(select(Product))
        return len(result.scalars().all())