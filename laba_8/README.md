# Лабораторная работа №8

1.Активируйте окружение: .venv\Scripts\activate (Windows) или source .venv\Scripts\activate (Linux/Mac)

2.Установите зависимости: pip install -r requirements.txt

3.Поднимите контейнеры docker compose build docker compose up -d

4.docker compose exec app python init_db.py
docker compose exec app alembic upgrade head

5. Проверка REST API
http://localhost:8000/users — пользователи
http://localhost:8000/products — продукты
http://localhost:8000/orders — заказы

7. Мониторинг логов воркера (задача выполняется каждую минуту)
docker compose logs taskiq-worker 
docker compose logs taskiq-scheduler 
9. Проверка эндпоинта /report
GET http://localhost:8000/report?date=2025-12-16
