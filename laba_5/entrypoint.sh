#!/bin/bash

set -e

# Запускаем миграции Alembic (если они есть)
echo "Запуск миграций Alembic..."
python -m alembic upgrade head

# Запускаем приложение
echo "Запуск приложения..."
exec python main.py