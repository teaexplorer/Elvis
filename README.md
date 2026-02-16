# Achievements API

REST API сервис для управления достижениями пользователей с поддержкой мультиязычности (русский/английский). Проект разработан на FastAPI с использованием PostgreSQL и Nginx.

## Содержание

- [Achievements API](#achievements-api)
  - [Содержание](#содержание)
  - [Технологии](#технологии)
  - [Функциональность](#функциональность)
  - [Установка и запуск](#установка-и-запуск)
    - [Предварительные требования](#предварительные-требования)
    - [Запуск с Docker](#запуск-с-docker)
    - [Тесты](#тесты)
- [Установка зависимостей для тестов](#установка-зависимостей-для-тестов)
- [Запуск всех тестов](#запуск-всех-тестов)
- [Запуск с coverage отчетом](#запуск-с-coverage-отчетом)
- [Запуск конкретного файла](#запуск-конкретного-файла)
- [Запуск конкретного теста](#запуск-конкретного-теста)
- [Запуск с подробным выводом](#запуск-с-подробным-выводом)

## Технологии

- Python 3.11
- FastAPI
- SQLAlchemy 2.0
- PostgreSQL 15
- Docker & Docker Compose
- Nginx
- Poetry (управление зависимостями)
- Pydantic 2.0

## Функциональность

- Управление пользователями (создание, просмотр)
- Управление достижениями (создание, просмотр)
- Выдача достижений пользователям
- Мультиязычность (автоматический перевод названий и описаний)
- Статистика и аналитика:
  - Пользователь с максимальным количеством достижений
  - Пользователь с максимальным количеством очков
  - Пользователи с максимальной разницей в очках
  - Пользователи с минимальной разницей в очках
  - Пользователи с 7-дневным стриком получения достижений
- Автоматическая документация Swagger/ReDoc

## Установка и запуск

### Предварительные требования

- Docker и Docker Compose (для контейнеризации)
- Python 3.11+ (для локального запуска)
- Poetry (для управления зависимостями)
- PostgreSQL (при локальном запуске)

### Запуск с Docker

Клонируйте репозиторий:
```bash
git clone <repository-url>
cd achievements-project
```

Примеры запросов
Создание пользователя
Запрос:

bash
curl -X POST http://localhost:80/api/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "ivan_petrov",
    "language": "ru"
  }'
Ответ:

json
{
  "id": 1,
  "username": "ivan_petrov",
  "language": "ru",
  "created_at": "2024-01-15T10:30:00"
}

Создание достижения
Запрос:

bash
curl -X POST http://localhost:80/api/achievements/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Первый полет",
    "name_ru": "Первый полет",
    "name_en": "First Flight",
    "points": 100,
    "description": "Получите свое первое достижение",
    "description_ru": "Получите свое первое достижение",
    "description_en": "Get your first achievement"
  }'
Ответ:

json
{
  "id": 1,
  "name": "Первый полет",
  "name_ru": "Первый полет",
  "name_en": "First Flight",
  "points": 100,
  "description": "Получите свое первое достижение",
  "description_ru": "Получите свое первое достижение",
  "description_en": "Get your first achievement",
  "created_at": "2024-01-15T10:31:00"
}

Выдача достижения
Запрос:

bash
curl -X POST http://localhost:80/api/achievements/award/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "achievement_id": 1
  }'
Ответ:

json
{
  "id": 1,
  "user_id": 1,
  "achievement_id": 1,
  "awarded_at": "2024-01-15T10:32:00"
}

Получение достижений пользователя
Запрос:

bash
curl http://localhost:80/api/users/1/achievements/
Ответ (для пользователя с языком "ru"):

json
{
  "user_id": 1,
  "username": "ivan_petrov",
  "language": "ru",
  "achievements": [
    {
      "name": "Первый полет",
      "description": "Получите свое первое достижение",
      "points": 100,
      "awarded_at": "2024-01-15T10:32:00"
    }
  ]
}

Статистика
Максимальное количество достижений:

bash
curl http://localhost:80/api/stats/max-achievements/
Ответ:

json
{
  "user_id": 2,
  "username": "john_doe",
  "total_achievements": 5
}

Максимальная разница в очках:

bash
curl http://localhost:80/api/stats/max-difference/
Ответ:

json
{
  "user1_id": 1,
  "user1_name": "ivan_petrov",
  "user2_id": 2,
  "user2_name": "john_doe",
  "difference": 450
}


### Тесты
# Установка зависимостей для тестов
poetry add --group test pytest pytest-cov pytest-mock httpx

# Запуск всех тестов
poetry run pytest tests/ -v

# Запуск с coverage отчетом
poetry run pytest tests/ --cov=. --cov-report=html -v

# Запуск конкретного файла
poetry run pytest tests/test_api.py -v

# Запуск конкретного теста
poetry run pytest tests/test_api.py::TestUserEndpoints::test_create_user_success -v

# Запуск с подробным выводом
poetry run pytest tests/ -v -s