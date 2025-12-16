# tests/test_routes/test_order_routes.py
import pytest


@pytest.mark.asyncio
def test_create_order(client):  
    """Тестирует создание заказа через API."""
    # Подготовим данные для запроса
    user_data = {"username": "Test User", "email": "test@example.com"}
    user_response = client.post("/users/create_user", json=user_data)  
    assert user_response.status_code == 201
    user = user_response.json()

    product_data = {"name": "Test Product", "price": 100.0, "stock_quantity": 10}
    product_response = client.post("/products", json=product_data)  
    assert product_response.status_code == 201
    product = product_response.json()

    order_data = {
        "user_id": user["id"],
        "product_ids": [product["id"]]
    }

    response = client.post("/orders", json=order_data)  

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["user_id"] == user["id"]
    assert data["status"] == "pending"


@pytest.mark.asyncio
def test_get_order_by_id(client):  
    """Тестирует получение заказа по ID через API."""
    # Сначала создадим пользователя и продукт
    user_data = {"username": "Test User", "email": "test@example.com"}
    user_response = client.post("/users/create_user", json=user_data)  
    assert user_response.status_code == 201
    user = user_response.json()

    product_data = {"name": "Test Product", "price": 100.0, "stock_quantity": 10}
    product_response = client.post("/products", json=product_data)  
    assert product_response.status_code == 201
    product = product_response.json()

    # Создаём заказ
    order_data = {
        "user_id": user["id"],
        "product_ids": [product["id"]]
    }
    order_response = client.post("/orders", json=order_data)  
    assert order_response.status_code == 201
    created_order = order_response.json()

    # Получаем заказ по ID
    response = client.get(f"/orders/{created_order['id']}")  

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created_order["id"]
    assert data["user_id"] == user["id"]


@pytest.mark.asyncio
def test_get_orders_list(client):  
    """Тестирует получение списка заказов через API."""
    response = client.get("/orders")  

    assert response.status_code == 200
    data = response.json()
    assert "orders" in data
    assert isinstance(data["orders"], list)


@pytest.mark.asyncio
def test_update_order_status(client):  
    """Тестирует обновление статуса заказа через API."""
    # Сначала создадим пользователя и продукт
    user_data = {"username": "Test User", "email": "test@example.com"}
    user_response = client.post("/users/create_user", json=user_data)  
    assert user_response.status_code == 201
    user = user_response.json()

    product_data = {"name": "Test Product", "price": 100.0, "stock_quantity": 10}
    product_response = client.post("/products", json=product_data)  
    assert product_response.status_code == 201
    product = product_response.json()

    # Создаём заказ
    order_data = {
        "user_id": user["id"],
        "product_ids": [product["id"]]
    }
    order_response = client.post("/orders", json=order_data)  
    assert order_response.status_code == 201
    created_order = order_response.json()

    # Обновляем статус
    update_data = {"status": "completed"}
    response = client.put(f"/orders/{created_order['id']}/status", json=update_data)  

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"


@pytest.mark.asyncio
def test_delete_order(client):  
    """Тестирует удаление заказа через API."""
    # Сначала создадим пользователя и продукт
    user_data = {"username": "Test User", "email": "test@example.com"}
    user_response = client.post("/users/create_user", json=user_data)  
    assert user_response.status_code == 201
    user = user_response.json()

    product_data = {"name": "Test Product", "price": 100.0, "stock_quantity": 10}
    product_response = client.post("/products", json=product_data)  
    assert product_response.status_code == 201
    product = product_response.json()

    # Создаём заказ
    order_data = {
        "user_id": user["id"],
        "product_ids": [product["id"]]
    }
    order_response = client.post("/orders", json=order_data)  
    assert order_response.status_code == 201
    created_order = order_response.json()

    # Удаляем заказ
    response = client.delete(f"/orders/{created_order['id']}")  

    assert response.status_code == 204  

    # Проверим, что заказа больше нет
    get_response = client.get(f"/orders/{created_order['id']}")  
    assert get_response.status_code == 404