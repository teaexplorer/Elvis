#!/bin/bash
set -e

echo "=== Проверка подключения к БД ==="
echo "Ждем базу данных ${DB_HOST}:${DB_PORT}..."
while ! nc -z ${DB_HOST} ${DB_PORT}; do
  sleep 1
done
echo "База данных доступна"

echo "=== Создание таблиц ==="
python -c "
import sys
print('Импорт модулей...')
from db.database import engine, Base
from db import db_models
print('Модули импортированы')
print('Создание таблиц...')
Base.metadata.create_all(bind=engine)
print('Таблицы созданы успешно!')
sys.exit(0)
"

echo "=== Запуск приложения ==="
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload