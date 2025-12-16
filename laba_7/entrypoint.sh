#!/bin/bash

set -e

echo "========== STARTING APPLICATION =========="
echo "Time: $(date)"

# 1. Ждем PostgreSQL
echo "1. Waiting for PostgreSQL..."
while ! nc -z postgres 5432; do sleep 1; done
echo "PostgreSQL is ready (takes ~5 seconds)"


echo "2. Waiting for RabbitMQ..."
echo "   RabbitMQ takes 25+ seconds to fully start..."
echo "   Step 1: Waiting for port to open..."
while ! nc -z rabbitmq 5672; do sleep 2; done
echo " RabbitMQ port is open (~15 seconds)"

echo "   Step 2: Giving RabbitMQ 40 seconds to fully initialize..."
sleep 40 

echo "   Step 3: Final check..."
if nc -z rabbitmq 5672; then
    echo "RabbitMQ is fully ready!"
else
    echo "RabbitMQ still not ready"
    exit 1
fi

# 3. Миграции
echo "3. Running migrations..."
alembic upgrade head 2>/dev/null || echo "⚠ Could not run migrations"

# 4. Запуск приложения
echo "4. Starting application..."
echo "Server: http://localhost:8000"
echo "RabbitMQ Management: http://localhost:15672 (guest/guest)"
echo "PostgreSQL: localhost:5432 (postgres/postgres)"
echo "=========================================="
echo "If app fails, check logs: docker-compose logs app"
echo "=========================================="

exec python main.py