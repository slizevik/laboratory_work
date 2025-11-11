import requests
import json

BASE_URL = "http://localhost:8000"


def debug_response():
    print("=== ОТЛАДКА ОТВЕТА СЕРВЕРА ===")

    # 1. Создаем пользователя и смотрим полный ответ
    user_data = {"username": "debug_user", "email": "debug@example.com"}

    try:
        response = requests.post(f"{BASE_URL}/users", json=user_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Full Response: {response.text}")

        if response.status_code == 200:
            user = response.json()
            print(f"✅ Response JSON: {json.dumps(user, indent=2)}")
            print(f"✅ Available keys: {list(user.keys())}")
        else:
            print(f"❌ Error: {response.text}")

    except Exception as e:
        print(f"❌ Exception: {e}")


if __name__ == "__main__":
    debug_response()