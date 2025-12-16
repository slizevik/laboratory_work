# controllers/order_controller.py
from litestar import Controller, get, post, put, delete
from litestar.di import Provide
from litestar.params import Parameter, Body
from litestar.exceptions import NotFoundException, ValidationException
from schemas.order import OrderCreate, OrderUpdate, OrderResponse
from services.order_service import OrderService

class OrderController(Controller):
    path = "/orders"

    @get("/{order_id:str}")
    async def get_order(
        self,
        order_service: OrderService,
        order_id: str = Parameter(description="ID заказа"),
    ) -> OrderResponse:
        order = await order_service.get_by_id(order_id)
        if not order:
            raise NotFoundException(detail=f"Order with ID {order_id} not found")
        return OrderResponse.model_validate(order)

    @get()
    async def list_orders(
        self,
        order_service: OrderService,
        count: int = Parameter(gt=0, le=100, default=10),
        page: int = Parameter(gt=0, default=1),
    ) -> dict:
        orders = await order_service.get_all(count=count, page=page)
        total = await order_service.get_total_count()
        return {
            "orders": [OrderResponse.model_validate(o) for o in orders],
            "total_count": total,
            "page": page,
            "count": count,
        }

    @post()
    async def create_order(
        self,
        order_service: OrderService,
        data: OrderCreate = Body(description="Данные для создания заказа"),
    ) -> OrderResponse:
        try:
            order = await order_service.create(data)
            return OrderResponse.model_validate(order)
        except ValueError as e:
            raise ValidationException(detail=str(e))

    @put("/{order_id:str}/status")
    async def update_order_status(
        self,
        order_service: OrderService,
        order_id: str,
        data: OrderUpdate = Body(description="Новый статус заказа"),
    ) -> OrderResponse:
        try:
            order = await order_service.update_status(order_id, data.status)
            if not order:
                raise NotFoundException(detail=f"Order with ID {order_id} not found")
            return OrderResponse.model_validate(order)
        except ValueError as e:
            raise ValidationException(detail=str(e))

    @delete("/{order_id:str}")
    async def delete_order(
        self,
        order_service: OrderService,
        order_id: str,
    ) -> None:
        success = await order_service.delete(order_id)
        if not success:
            raise NotFoundException(detail=f"Order with ID {order_id} not found")