# Лабораторная работа №7

1.Активируйте окружение: .venv\Scripts\activate (Windows) или source .venv\Scripts\activate (Linux/Mac)

2.Установите зависимости: pip install -r requirements.txt

3.Поднимите контейнеры
docker compose build 
docker compose up -d

4.Можно проверить работу тестовых скриптов для Redis
docker-compose exec app python test_redis.py
docker-compose exec app python redis_data_structures.py

5. Запросы в терминал для проверки
   5.1. Создать пользователя
$createUser = @{ username="cache_user"; email="cache_user@example.com" }
$res = Invoke-WebRequest -Uri http://localhost:8000/users/create_user -Method Post -ContentType "application/json" -UseBasicParsing -Body ($createUser | ConvertTo-Json -Compress) | Select-Object -ExpandProperty Content  
Создаёт нового пользователя и сохраняет JSON-ответ.

   5.2. Извлечь ID пользователя
$userId = (ConvertFrom-Json $res).id  
Получает идентификатор созданного пользователя из ответа.

    5.3. Первый запрос данных (сохранение в кэш)
Invoke-WebRequest -Uri ("http://localhost:8000/users/{0}" -f $userId) -UseBasicParsing | Select-Object -ExpandProperty Content  
Запрашивает данные — они читаются из БД и кэшируются на 1 час.

    5.4. Повторный запрос (чтение из кэша)
Invoke-WebRequest -Uri ("http://localhost:8000/users/{0}" -f $userId) -UseBasicParsing | Select-Object -ExpandProperty Content  
Повторно запрашивает те же данные — теперь они берутся из кэша.

    5.5. Обновить пользователя (инвалидация кэша)
$updateUser = @{ username="cache_user_updated" }
Invoke-WebRequest -Uri ("http://localhost:8000/users/{0}" -f $userId) -Method Put -ContentType "application/json" -UseBasicParsing -Body ($updateUser | ConvertTo-Json -Compress) | Select-Object -ExpandProperty Content  
Обновляет данные пользователя и удаляет старую запись из кэша.

    5.6. Запрос после обновления (новая запись в кэш)
Invoke-WebRequest -Uri ("http://localhost:8000/users/{0}" -f $userId) -UseBasicParsing | Select-Object -ExpandProperty Content  
Повторно запрашивает данные — теперь они из БД, а затем снова попадают в кэш.


6. Продукты: аналогично, TTL 10 минут; обновление перезаписывает кэш.
   6.1 Создать
$createProduct = @{ name = "cached product"; description = "desc"; price = 10.5; stock_quantity = 5 }
$resP = Invoke-WebRequest -Uri http://localhost:8000/products `
  -Method Post -ContentType "application/json" -UseBasicParsing `
  -Body ($createProduct | ConvertTo-Json -Compress) | Select-Object -ExpandProperty Content
$productId = (ConvertFrom-Json $resP).id

  6.2 Первый GET (ставит в кэш)
Invoke-WebRequest -Uri ("http://localhost:8000/products/{0}" -f $productId) -UseBasicParsing |
  Select-Object -ExpandProperty Content

  6.3 Второй GET (из кэша)
Invoke-WebRequest -Uri ("http://localhost:8000/products/{0}" -f $productId) -UseBasicParsing |
  Select-Object -ExpandProperty Content

  6.4 Обновить (перезапишет кэш)
$updateProduct = @{ price = 12.0 }
Invoke-WebRequest -Uri ("http://localhost:8000/products/{0}" -f $productId) `
  -Method Put -ContentType "application/json" -UseBasicParsing `
  -Body ($updateProduct | ConvertTo-Json -Compress) |
  Select-Object -ExpandProperty Content

  6.5 GET после обновления
Invoke-WebRequest -Uri ("http://localhost:8000/products/{0}" -f $productId) -UseBasicParsing |
  Select-Object -ExpandProperty Content
