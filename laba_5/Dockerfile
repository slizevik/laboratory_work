FROM python:3.11-slim

WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем зависимости по одному пакету, чтобы не перегружать память
RUN pip install --no-cache-dir asyncpg
RUN pip install --no-cache-dir uvicorn
RUN pip install --no-cache-dir pydantic
RUN pip install --no-cache-dir psycopg
RUN pip install --no-cache-dir sqlalchemy
RUN pip install --no-cache-dir litestar
RUN pip install --no-cache-dir "pydantic[email]"

# Остальные зависимости (тестовые) можно установить отдельно или убрать, если не нужны для запуска
# RUN pip install --no-cache-dir pytest pytest-asyncio pytest-cov httpx freezegun requests

# Копируем остальные файлы проекта
COPY . .

# Указываем команду по умолчанию (она будет переопределена в entrypoint.sh)
CMD ["sh", "-c", "./entrypoint.sh"]