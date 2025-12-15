# План тестирования и запуска приложения

## Описание системы

Приложение состоит из следующих компонентов:
- **PostgreSQL** - база данных (порт 5432)
- **RabbitMQ** - брокер сообщений (порты 5672, 15672)
- **App** - веб-приложение на Litestar с FastStream (порт 8000)
- **Producer** - скрипт для отправки сообщений в RabbitMQ

---

## Шаг 1: Подготовка окружения

### 1.1. Переход в директорию проекта
```powershell
cd "C:\DATA BOSS\laba_6_git"
```

### 1.2. Проверка наличия файлов
Убедитесь, что присутствуют следующие файлы:
- `docker-compose.yml`
- `Dockerfile`
- `main.py`
- `producer.py`
- `requirements.txt`

---

## Шаг 2: Сборка Docker-образов

### 2.1. Сборка образов для всех сервисов
```powershell
docker compose build
```

**Ожидаемый результат:**
- Успешная сборка образа для сервиса `app`
- Скачивание образов `postgres:13` и `rabbitmq:3-management` (если их нет)

**Время выполнения:** ~2-5 минут (в зависимости от скорости интернета)

---

## Шаг 3: Запуск контейнеров

### 3.1. Запуск всех сервисов
```powershell
docker compose up -d
```

**Что происходит:**
- Запускается контейнер `postgres` (база данных)
- Запускается контейнер `rabbitmq` (брокер сообщений)
- Запускается контейнер `app` (веб-приложение)

**Флаг `-d`** запускает контейнеры в фоновом режиме (detached mode)

### 3.2. Проверка статуса контейнеров
```powershell
docker compose ps
```

**Ожидаемый результат:**
```
NAME                    STATUS
laba_6_git-postgres-1   Up
laba_6_git-rabbitmq-1   Up
laba_6_git-app-1        Up
```

### 3.3. Ожидание полной инициализации (важно!)
Подождите **~60 секунд** для полной инициализации:
- PostgreSQL готовится ~5 секунд
- RabbitMQ готовится ~40-60 секунд
- App запускается и подключается к сервисам

**Проверка готовности:**
```powershell
docker compose logs app
```

Ищите строки:
- `PostgreSQL is ready`
- `RabbitMQ is fully ready!`
- `Запуск сервера с FastStream и Litestar на http://0.0.0.0:8000`
- `Брокер RabbitMQ запущен`

---

## Шаг 4: Проверка доступности сервисов

### 4.1. Проверка веб-приложения
```powershell
Invoke-WebRequest -Uri http://localhost:8000/users -UseBasicParsing | Select-Object -ExpandProperty Content
```

**Ожидаемый результат:** JSON с массивом пользователей или пустым массивом `{"users":[],"total_count":0,"page":1,"count":10}`

### 4.2. Проверка RabbitMQ Management UI
Откройте в браузере: `http://localhost:15672`
- **Логин:** `app`
- **Пароль:** `app`

Проверьте наличие vhost `local` и очередей `order` и `product`

---

## Шаг 5: Запуск Producer (отправка сообщений)

### 5.1. Запуск producer внутри контейнера app
```powershell
docker compose exec app python producer.py
```

**Ожидаемый результат:**
```
Отправка 5 сообщений о продукции...
  Отправлено: {'id': 1, 'name': 'Product 1', 'price': 45.23, 'quantity': 67}
  Отправлено: {'id': 2, 'name': 'Product 2', 'price': 78.91, 'quantity': 34}
  ...
Отправка 3 сообщений о заказах...
  Отправлено: {'id': 1, 'user_id': 5, 'items': [...], 'status': 'pending'}
  ...
Все сообщения отправлены.
```

### 5.2. Проверка обработки сообщений
```powershell
docker compose logs app
```

**Ожидаемый результат в логах:**
```
Получена продукция: {'id': 1, 'name': 'Product 1', ...}
Продукция обработана.
Получен заказ: {'id': 1, 'user_id': 5, ...}
Заказ обработан.
```

---

## Шаг 6: Тестирование REST API

### 6.1. Тестирование эндпоинтов Users

#### 6.1.1. Получение списка пользователей
```powershell
Invoke-WebRequest -Uri http://localhost:8000/users -UseBasicParsing | Select-Object -ExpandProperty Content
```

#### 6.1.2. Создание пользователя
```powershell
$body = @{
    name = "Test User"
    email = "test@example.com"
} | ConvertTo-Json

Invoke-WebRequest -Uri http://localhost:8000/users/create_user -Method POST -Body $body -ContentType "application/json" -UseBasicParsing | Select-Object -ExpandProperty Content
```

#### 6.1.3. Получение пользователя по ID
```powershell
# Замените {user_id} на реальный ID из предыдущего запроса
Invoke-WebRequest -Uri http://localhost:8000/users/{user_id} -UseBasicParsing | Select-Object -ExpandProperty Content
```

### 6.2. Тестирование эндпоинтов Products

#### 6.2.1. Получение списка продуктов
```powershell
Invoke-WebRequest -Uri http://localhost:8000/products -UseBasicParsing | Select-Object -ExpandProperty Content
```

#### 6.2.2. Создание продукта
```powershell
$body = @{
    name = "Test Product"
    price = 99.99
    quantity = 10
} | ConvertTo-Json

Invoke-WebRequest -Uri http://localhost:8000/products -Method POST -Body $body -ContentType "application/json" -UseBasicParsing | Select-Object -ExpandProperty Content
```

#### 6.2.3. Получение продукта по ID
```powershell
Invoke-WebRequest -Uri http://localhost:8000/products/{product_id} -UseBasicParsing | Select-Object -ExpandProperty Content
```

### 6.3. Тестирование эндпоинтов Orders

#### 6.3.1. Получение списка заказов
```powershell
Invoke-WebRequest -Uri http://localhost:8000/orders -UseBasicParsing | Select-Object -ExpandProperty Content
```

#### 6.3.2. Создание заказа
```powershell
$body = @{
    user_id = "1"
    items = @(
        @{
            product_id = "1"
            quantity = 2
        }
    )
    status = "pending"
} | ConvertTo-Json

Invoke-WebRequest -Uri http://localhost:8000/orders -Method POST -Body $body -ContentType "application/json" -UseBasicParsing | Select-Object -ExpandProperty Content
```

---

## Шаг 7: Проверка интеграции компонентов

### 7.1. Проверка работы RabbitMQ
1. Откройте `http://localhost:15672`
2. Перейдите в раздел **Queues**
3. Проверьте очереди `order` и `product`
4. Убедитесь, что сообщения обрабатываются (счетчики сообщений)

### 7.2. Проверка работы базы данных
```powershell
# Проверка подключения к PostgreSQL через Docker
docker compose exec postgres psql -U postgres -d postgres -c "SELECT COUNT(*) FROM users;"
docker compose exec postgres psql -U postgres -d postgres -c "SELECT COUNT(*) FROM products;"
docker compose exec postgres psql -U postgres -d postgres -c "SELECT COUNT(*) FROM orders;"
```

---

## Шаг 8: Остановка и очистка

### 8.1. Остановка контейнеров
```powershell
docker compose down
```

### 8.2. Остановка с удалением volumes (полная очистка)
```powershell
docker compose down -v
```

**Внимание:** Это удалит все данные из базы данных и RabbitMQ!

---

## Чеклист успешного тестирования

- [ ] Все контейнеры успешно запущены (`docker compose ps`)
- [ ] Веб-приложение отвечает на `http://localhost:8000/users`
- [ ] Producer успешно отправляет сообщения
- [ ] App успешно получает и обрабатывает сообщения из RabbitMQ
- [ ] REST API эндпоинты работают корректно
- [ ] Данные сохраняются в базе данных
- [ ] RabbitMQ Management UI доступен

---

## Возможные проблемы и решения

### Проблема: ERR_EMPTY_RESPONSE при обращении к localhost:8000
**Решение:** 
- Проверьте логи: `docker compose logs app`
- Убедитесь, что контейнер `app` в статусе `Up`
- Подождите полной инициализации (~60 секунд)

### Проблема: PRECONDITION_FAILED при запуске producer
**Решение:**
- Удалите существующие очереди в RabbitMQ Management UI
- Или перезапустите RabbitMQ: `docker compose restart rabbitmq`

### Проблема: Контейнер app постоянно перезапускается
**Решение:**
- Проверьте логи: `docker compose logs app`
- Убедитесь, что PostgreSQL и RabbitMQ полностью инициализированы
- Проверьте переменные окружения в `docker-compose.yml`

---

## Дополнительные команды для диагностики

```powershell
# Просмотр логов конкретного сервиса
docker compose logs app
docker compose logs rabbitmq
docker compose logs postgres

# Просмотр логов в реальном времени
docker compose logs -f app

# Перезапуск конкретного сервиса
docker compose restart app

# Выполнение команды внутри контейнера
docker compose exec app python -c "print('Hello from container')"
```

---

## Структура API эндпоинтов

### Users (`/users`)
- `GET /users` - список пользователей с пагинацией
- `GET /users/{user_id}` - получение пользователя по ID
- `POST /users/create_user` - создание пользователя
- `PUT /users/{user_id}` - обновление пользователя
- `DELETE /users/{user_id}` - удаление пользователя

### Products (`/products`)
- `GET /products` - список продуктов с пагинацией
- `GET /products/{product_id}` - получение продукта по ID
- `POST /products` - создание продукта
- `PUT /products/{product_id}` - обновление продукта

### Orders (`/orders`)
- `GET /orders` - список заказов с пагинацией
- `GET /orders/{order_id}` - получение заказа по ID
- `POST /orders` - создание заказа
- `PUT /orders/{order_id}/status` - обновление статуса заказа

---

**Дата создания:** 2025-12-16  
**Версия:** 1.0

