# tests/test_routes/test_user_routes.py
import pytest


@pytest.mark.asyncio
def test_create_user(client):
    """Тестирует создание пользователя через API."""
    user_data = {
        "username": "Test User",
        "email": "test@example.com"
    }

    response = client.post("/users/create_user", json=user_data)

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["username"] == "Test User"
    assert data["email"] == "test@example.com"


@pytest.mark.asyncio
def test_get_user_by_id(client):
    """Тестирует получение пользователя по ID через API."""
    # Сначала создадим пользователя
    user_data = {
        "username": "Test User",
        "email": "test@example.com"
    }
    user_response = client.post("/users/create_user", json=user_data)
    assert user_response.status_code == 201
    created_user = user_response.json()

    # Получаем пользователя по ID
    response = client.get(f"/users/{created_user['id']}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created_user["id"]
    assert data["username"] == "Test User"


@pytest.mark.asyncio
def test_get_users_list(client):
    """Тестирует получение списка пользователей через API."""
    response = client.get("/users")

    assert response.status_code == 200
    data = response.json()
    assert "users" in data
    assert isinstance(data["users"], list)


def test_update_user(client):  
    """Тестирует обновление пользователя через API."""
    # Сначала создадим пользователя
    user_data = {
        "username": "Original User",
        "email": "original@example.com"
    }
    user_response = client.post("/users/create_user", json=user_data)
    assert user_response.status_code == 201
    created_user = user_response.json()

    # Обновляем пользователя (передаём оба поля, даже если не все меняются)
    update_data = {
        "username": "Updated User",
     #   "email": created_user["email"]  # ← Передаём старый email, чтобы не было None
    }
    response = client.put(f"/users/{created_user['id']}", json=update_data)

    
    print("Response status:", response.status_code)
    print("Response body:", response.text)

    assert response.status_code == 200  
    data = response.json()
    assert data["username"] == "Updated User"


@pytest.mark.asyncio
def test_delete_user(client):
    """Тестирует удаление пользователя через API."""
    # Сначала создадим пользователя
    user_data = {
        "username": "To Delete",
        "email": "delete@example.com"
    }
    user_response = client.post("/users/create_user", json=user_data)
    assert user_response.status_code == 201
    created_user = user_response.json()

    # Удаляем пользователя
    response = client.delete(f"/users/{created_user['id']}")

    assert response.status_code == 204  

    # Проверим, что пользователя больше нет
    get_response = client.get(f"/users/{created_user['id']}")
    assert get_response.status_code == 404