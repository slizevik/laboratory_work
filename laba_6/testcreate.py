import requests
import json

url = "http://localhost:8000/users/create_user"

# Данные для body
body_data = {
    "username": "Ekaterina Koreneva",
    "email": "ekatkoren@example.com"
}

response = requests.post(
    url,
    json=body_data
)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
