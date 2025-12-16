# tests/test_routes/test_product_routes.py
import pytest


@pytest.mark.asyncio
def test_create_product(client):
    """Тестирует создание продукта через API."""
    product_data = {
        "name": "Test Product",
        "description": "A product for testing",
        "price": 100.0,
        "stock_quantity": 10
    }

    response = client.post("/products", json=product_data)

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["name"] == "Test Product"
    assert data["price"] == 100.0
    assert data["stock_quantity"] == 10


@pytest.mark.asyncio
def test_get_product_by_id(client):
    """Тестирует получение продукта по ID через API."""
    # Сначала создадим продукт
    product_data = {
        "name": "Test Product",
        "description": "A product for testing",
        "price": 100.0,
        "stock_quantity": 10
    }
    product_response = client.post("/products", json=product_data)
    assert product_response.status_code == 201
    created_product = product_response.json()

    # Получаем продукт по ID
    response = client.get(f"/products/{created_product['id']}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created_product["id"]
    assert data["name"] == "Test Product"


@pytest.mark.asyncio
def test_get_products_list(client):
    """Тестирует получение списка продуктов через API."""
    response = client.get("/products")

    assert response.status_code == 200
    data = response.json()
    assert "products" in data
    assert isinstance(data["products"], list)


@pytest.mark.asyncio
def test_update_product(client):
    """Тестирует обновление продукта через API."""
    # Сначала создадим продукт
    product_data = {
        "name": "Original Product",
        "description": "Original description",
        "price": 100.0,
        "stock_quantity": 10
    }
    product_response = client.post("/products", json=product_data)
    assert product_response.status_code == 201
    created_product = product_response.json()

    # Обновляем продукт
    update_data = {
        "name": "Updated Product",
        "price": 150.0
    }
    response = client.put(f"/products/{created_product['id']}", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Product"
    assert data["price"] == 150.0


@pytest.mark.asyncio
def test_delete_product(client):
    """Тестирует удаление продукта через API."""
    # Сначала создадим продукт
    product_data = {
        "name": "To Delete",
        "description": "A product for deletion",
        "price": 100.0,
        "stock_quantity": 5
    }
    product_response = client.post("/products", json=product_data)
    assert product_response.status_code == 201
    created_product = product_response.json()

    # Удаляем продукт
    response = client.delete(f"/products/{created_product['id']}")

    assert response.status_code == 204  # No Content

    # Проверим, что продукта больше нет
    get_response = client.get(f"/products/{created_product['id']}")
    assert get_response.status_code == 404
    