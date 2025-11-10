import requests

print("=== СОЗДАЕМ ТЕСТОВЫХ ПОЛЬЗОВАТЕЛЕЙ ===")

users_to_create = [
    {"username": "alex_dev", "email": "alex@example.com"},
    {"username": "maria_code", "email": "maria@example.com"},
    {"username": "john_tech", "email": "john@example.com"}
]

for user_data in users_to_create:
    try:
        response = requests.post("http://localhost:8000/users", json=user_data)
        if response.status_code == 200:
            user = response.json()
            print(f"✅ Создан: {user['username']}")
        else:
            print(f"❌ Ошибка с {user_data['username']}: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

print("\n=== ПРОВЕРЯЕМ ===")
response = requests.get("http://localhost:8000/users")
users = response.json()
print(f"✅ Теперь пользователей: {len(users)}")
