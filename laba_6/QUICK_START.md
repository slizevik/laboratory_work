# Быстрый старт - Краткая инструкция

## 1. Сборка и запуск
```powershell
cd "C:\DATA BOSS\laba_6_git"
docker compose build
docker compose up -d
```

## 2. Проверка статуса (подождите ~60 сек)
```powershell
docker compose ps
docker compose logs app
```

## 3. Запуск Producer
```powershell
docker compose exec app python producer.py
```

## 4. Тестирование API
```powershell
# Проверка Users
Invoke-WebRequest -Uri http://localhost:8000/users -UseBasicParsing | Select-Object -ExpandProperty Content

# Проверка Products
Invoke-WebRequest -Uri http://localhost:8000/products -UseBasicParsing | Select-Object -ExpandProperty Content

# Проверка Orders
Invoke-WebRequest -Uri http://localhost:8000/orders -UseBasicParsing | Select-Object -ExpandProperty Content
```

## 5. Остановка
```powershell
docker compose down
```

---
Подробная инструкция: см. `TESTING_PLAN.md`

