# SmartBank API Gateway

API-шлюз для проекта **SmartBank**. Сервис выступает единой точкой входа для клиентских запросов: принимает HTTP-запросы, сохраняет состояние задач в PostgreSQL и маршрутизирует задачи в Kafka для дальнейшей асинхронной обработки RAG-воркерами и другими микросервисами.

---

## Содержание

- [Архитектура и принцип работы](#архитектура-и-принцип-работы)
- [Стек технологий](#стек-технологий)
- [Структура проекта](#структура-проекта)
- [Установка и подготовка окружения](#установка-и-подготовка-окружения)
- [Конфигурация](#конфигурация)
- [Миграции базы данных](#миграции-базы-данных)
- [Запуск приложения](#запуск-приложения)
- [Тестирование и качество кода](#тестирование-и-качество-кода)
- [API](#api)
- [Статусы задач](#статусы-задач)

---

## Архитектура и принцип работы

Основной сценарий работы шлюза построен вокруг асинхронной обработки задач через Kafka.

```text
┌──────────┐
│  Client  │
└────┬─────┘
     │
     │ POST /ask
     ▼
┌─────────────────────┐
│  SmartBank Gateway  │
│      FastAPI        │
└────┬───────────┬────┘
     │           │
     │           │ сохраняет задачу
     │           ▼
     │      ┌──────────────┐
     │      │  PostgreSQL  │
     │      └──────────────┘
     │
     │ публикует task
     ▼
┌─────────────────────┐
│        Kafka        │
│  gateway-requests   │
└─────────┬───────────┘
          │
          ▼
   ┌───────────────┐
   │  RAG Worker   │
   └───────┬───────┘
           │
           │ результат
           ▼
┌─────────────────────┐
│        Kafka        │
│  worker-responses   │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  SmartBank Gateway  │
│  FastStream Handler │
└─────────┬───────────┘
          │
          │ обновление задачи
          ▼
   ┌──────────────┐
   │  PostgreSQL  │
   └──────────────┘
```

### Последовательность обработки

1. Клиент отправляет вопрос через `POST /ask`.
2. Gateway генерирует уникальный `task_id` в формате UUID.
3. Задача сохраняется в PostgreSQL со статусом `PENDING`.
4. Gateway публикует сообщение в Kafka в топик `gateway-requests`.
5. Клиент получает `task_id` и может проверять состояние задачи через `GET /status/{task_id}`.
6. Фоновый Kafka-подписчик, реализованный через FastStream, слушает топик `worker-responses`.
7. После получения результата от RAG-воркера Gateway обновляет задачу в PostgreSQL:
   - устанавливает статус `COMPLETED`;
   - сохраняет результат обработки.
8. Клиент получает готовый ответ при следующем запросе статуса.

---

## Стек технологий

| Категория | Технологии |
|---|---|
| Язык | Python 3.12+ |
| Менеджер пакетов | `uv` |
| Web-фреймворк | FastAPI |
| База данных | PostgreSQL |
| ORM | SQLAlchemy |
| Async DB driver | asyncpg |
| Миграции | Alembic |
| Векторное расширение | pgvector |
| Векторный тип | `Vector(1536)` |
| Message Broker | Apache Kafka |
| Kafka framework | FastStream |
| Валидация | Pydantic v2 |
| Конфигурация | Pydantic Settings |
| Линтинг | Ruff |
| Git hooks | pre-commit |
| Тестирование | pytest |
| Async-тесты | pytest-asyncio |
| Контейнеризация | Docker / Docker Compose |

---

## Структура проекта

```text
gateway/
│
├── alembic/                         # Инфраструктура миграций БД
│   ├── versions/                    # Файлы миграций
│   ├── env.py                       # Конфигурация Alembic + SQLAlchemy
│   ├── README
│   └── script.py.mako
│
├── app/                             # Исходный код Gateway
│   ├── __init__.py
│   ├── api.py                       # HTTP-роутеры FastAPI
│   ├── broker.py                    # Инициализация KafkaBroker / FastStream
│   ├── config.py                    # Конфигурация и .env
│   ├── database.py                  # Async Engine, connection pool, get_db()
│   ├── kafka_handlers.py            # FastStream subscribers
│   ├── main.py                      # ASGI-точка входа FastAPI
│   ├── models.py                    # SQLAlchemy-модели
│   └── schemas.py                   # Pydantic-схемы
│
├── scripts/
│   └── check_code.py                # Проверка закомментированного кода
│
├── tests/                            # Автотесты
│   ├── conftest.py                  # Фикстуры async-клиента и mock-объектов
│   ├── subscriber_test.py           # Тесты FastStream handlers
│   ├── test_api.py                  # Тесты HTTP endpoints
│   └── test_schemas.py              # Тесты Pydantic-моделей
│
├── .env.example                     # Шаблон переменных окружения
├── .pre-commit-config.yaml          # Конфигурация pre-commit
├── alembic.ini                      # Конфигурация Alembic
├── docker-compose.yml               # Gateway + PostgreSQL + Kafka + Kafka UI
├── Dockerfile                       # Docker-образ Gateway
└── pyproject.toml                   # Зависимости и настройки проекта
```

---

## Установка и подготовка окружения

### 1. Установить `uv`

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Проверить установку:

```bash
uv --version
```

### 2. Перейти в директорию проекта

```bash
cd gateway
```

### 3. Установить зависимости

`uv` создаст виртуальное окружение и установит зависимости из `pyproject.toml`.

```bash
uv sync
```

### 4. Установить Git hooks

```bash
uv run pre-commit install
```

---

## Конфигурация

Создайте файл `.env` в корне проекта `gateway/`.

Пример:

```env
POSTGRES_USER=admin
POSTGRES_PASSWORD=root
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_DB=smartbank

KAFKA_HOST=localhost:9092
```

> **Важно:** реальные секреты и пароли не следует коммитить в Git. Для репозитория используйте `.env.example`.

---

## Настройки PostgreSQL Connection Pool

Настройки пула подключений SQLAlchemy находятся в `app/database.py`.

| Параметр | Значение | Назначение |
|---|---:|---|
| `pool_size` | `5` | Количество постоянных соединений |
| `max_overflow` | `10` | Максимальное количество дополнительных соединений при нагрузке |
| `pool_timeout` | `30` | Время ожидания свободного соединения, секунд |
| `pool_recycle` | `1800` | Пересоздание соединений каждые 30 минут |
| `pool_pre_ping` | `True` | Проверка соединения перед выдачей из пула |

### `get_db()`

`get_db()` — асинхронный генератор сессий SQLAlchemy.

При успешном выполнении операции выполняется `commit`, при возникновении ошибки — `rollback`.

---

## Миграции базы данных

Для работы с миграциями используется **Alembic**.

### Применить все миграции

```bash
uv run alembic upgrade head
```

### Создать новую миграцию

```bash
uv run alembic revision --autogenerate -m "add_new_table"
```

После создания миграции рекомендуется проверить сгенерированный файл вручную перед применением.

### Откатить последнюю миграцию

```bash
uv run alembic downgrade -1
```

---

## Запуск приложения

### Вариант 1 — Docker Compose

Рекомендуемый способ запуска полного окружения.

```bash
docker compose up --build -d
```

Проверить запущенные контейнеры:

```bash
docker compose ps
```

### Просмотр логов Gateway

```bash
docker compose logs -f api_gateway
```

### Остановка контейнеров

```bash
docker compose down
```

Если необходимо удалить также volumes:

```bash
docker compose down -v
```

> Команда `down -v` удаляет данные из Docker volumes, включая данные PostgreSQL.

---

### Вариант 2 — локальный запуск

Если PostgreSQL и Kafka уже запущены локально:

```bash
uv run uvicorn app.main:app --reload --port 8000
```

После запуска API будет доступен на:

```text
http://localhost:8000
```

Swagger UI:

```text
http://localhost:8000/docs
```

ReDoc:

```text
http://localhost:8000/redoc
```

---

## Тестирование и качество кода

### Запуск всех тестов

```bash
uv run pytest -v
```

### Запуск тестов внутри Docker-контейнера

```bash
docker compose exec api_gateway pytest -v
```

### Запуск всех pre-commit hooks

```bash
uv run pre-commit run --all-files
```

### Проверка закомментированного кода

```bash
uv run pre-commit run no-commented-code-blocks --all-files
```

### Ruff: проверка и автоматическое исправление

```bash
uv run ruff check --fix .
```

### Ruff: форматирование

```bash
uv run ruff format .
```

---

# API

## `POST /ask`

Создает новую задачу на обработку пользовательского вопроса.

### Request

```http
POST /ask
Content-Type: application/json
```

```json
{
  "query": "Как перевести деньги ИП без комиссии?"
}
```

### Response — `200 OK`

```json
{
  "task_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "PENDING"
}
```

### Что происходит внутри

После получения запроса Gateway:

1. валидирует входные данные через Pydantic;
2. генерирует `task_id`;
3. создает запись задачи в PostgreSQL;
4. устанавливает статус `PENDING`;
5. отправляет задачу в Kafka topic `gateway-requests`;
6. возвращает клиенту `task_id`.

---

## `GET /status/{task_id}`

Возвращает текущий статус задачи и результат обработки.

### Request

```http
GET /status/3fa85f64-5717-4562-b3fc-2c963f66afa6
```

### Response — задача в обработке

```json
{
  "task_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "PENDING",
  "result": null
}
```

### Response — задача завершена

```json
{
  "task_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "COMPLETED",
  "result": {
    "answer": "Перевод без комиссии возможен через Систему Быстрых Платежей в пределах лимита тарифа.",
    "sources": [
      "Памятка по тарифам и лимитам.md"
    ],
    "confidence": 0.95
  }
}
```

### Response — задача не найдена

**HTTP `404 Not Found`**

```json
{
  "detail": "Task not found"
}
```

---

## Статусы задач

На текущем этапе основной жизненный цикл задачи выглядит следующим образом:

```text
          ┌─────────┐
          │ PENDING │
          └────┬────┘
               │
               │ ответ от RAG Worker
               ▼
        ┌─────────────┐
        │  COMPLETED  │
        └─────────────┘
```

### `PENDING`

Задача создана и ожидает или уже находится в процессе асинхронной обработки.

### `COMPLETED`

RAG-воркер завершил обработку. Результат сохранен в PostgreSQL и доступен через `GET /status/{task_id}`.

---

## Kafka

Gateway использует два основных Kafka-топика.

| Topic | Направление | Назначение |
|---|---|---|
| `gateway-requests` | Gateway → Worker | Передача новых задач на обработку |
| `worker-responses` | Worker → Gateway | Получение результатов обработки |

### Поток сообщений

```text
Gateway
   │
   │ task
   ▼
gateway-requests
   │
   ▼
RAG Worker
   │
   │ result
   ▼
worker-responses
   │
   ▼
Gateway
   │
   ▼
PostgreSQL
```

Kafka используется для разделения синхронного HTTP API и асинхронной обработки задач.

---

## Разработка

Перед созданием Pull Request рекомендуется выполнить:

```bash
uv run pytest -v
uv run ruff check --fix .
uv run ruff format .
uv run pre-commit run --all-files
```

Также необходимо убедиться, что:

- миграции Alembic применяются без ошибок;
- новые изменения покрыты тестами;
- секреты не добавлены в репозиторий;
- `.env` не коммитится;
- API-контракты и Pydantic-схемы синхронизированы с клиентом и воркерами.

---

## Лицензия

Проект является внутренним компонентом SmartBank.
