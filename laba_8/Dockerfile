FROM python:3.11

WORKDIR /app

# Установка netcat (nc), необходимого для entrypoint.sh
RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x entrypoint.sh
 
# Используем скрипт entrypoint.sh для ожидания PostgreSQL и RabbitMQ
ENTRYPOINT ["./entrypoint.sh"]
