# controllers/product_controller.py
from litestar import Controller, get, post, put, delete
from litestar.di import Provide
from litestar.params import Parameter, Body
from litestar.exceptions import NotFoundException, ValidationException
from schemas.product import ProductCreate, ProductUpdate, ProductResponse
from services.product_service import ProductService

class ProductController(Controller):
    path = "/products"

    @get("/{product_id:str}")
    async def get_product(
        self,
        product_service: ProductService,
        product_id: str = Parameter(description="ID продукта"),
    ) -> ProductResponse:
        product = await product_service.get_by_id(product_id)
        if not product:
            raise NotFoundException(detail=f"Product with ID {product_id} not found")
        return ProductResponse.model_validate(product)

    @get()
    async def list_products(
        self,
        product_service: ProductService,
        count: int = Parameter(gt=0, le=100, default=10),
        page: int = Parameter(gt=0, default=1),
    ) -> dict:
        products = await product_service.get_all(count=count, page=page)
        total = await product_service.get_total_count()
        return {
            "products": [ProductResponse.model_validate(p) for p in products],
            "total_count": total,
            "page": page,
            "count": count,
        }

    @post()
    async def create_product(
        self,
        product_service: ProductService,
        data: ProductCreate = Body(),
    ) -> ProductResponse:
        try:
            product = await product_service.create(data)
            return ProductResponse.model_validate(product)
        except ValueError as e:
            raise ValidationException(detail=str(e))

    @put("/{product_id:str}")
    async def update_product(
        self,
        product_service: ProductService,
        product_id: str,
        data: ProductUpdate,
    ) -> ProductResponse:
        try:
            product = await product_service.update(product_id, data)
            if not product:
                raise NotFoundException(detail=f"Product with ID {product_id} not found")
            return ProductResponse.model_validate(product)
        except ValueError as e:
            raise ValidationException(detail=str(e))

    @delete("/{product_id:str}")
    async def delete_product(
        self,
        product_service: ProductService,
        product_id: str,
    ) -> None:
        success = await product_service.delete(product_id)
        if not success:
            raise NotFoundException(detail=f"Product with ID {product_id} not found")