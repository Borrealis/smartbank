# SmartBank API Gateway

API-шлюз для проекта SmartBank. Сервис выступает единой точкой входа для клиентских запросов: он принимает HTTP-запросы, сохраняет их состояние в базу данных и маршрутизирует в брокер сообщений Kafka для дальнейшей асинхронной обработки RAG-воркерами (или другими микросервисами).

## Как это работает (Функционал)
1. Клиент отправляет вопрос через `POST /ask`.
2. Шлюз генерирует уникальный `task_id`, сохраняет задачу в PostgreSQL со статусом `PENDING` и отправляет сообщение в Kafka (топик `gateway-requests`).
3. Клиент получает `task_id` и может проверять готовность через `GET /status/{task_id}`.
4. Фоновый процесс шлюза (через FastStream) слушает топик Kafka `worker-responses`.
5. Когда сторонний воркер обрабатывает запрос и присылает ответ в этот топик, шлюз перехватывает сообщение и обновляет статус и результат задачи в базе данных (например, на `COMPLETED`).

## Стек технологий
- **Фреймворк:** FastAPI
- **База данных:** PostgreSQL, SQLAlchemy (async), pgvector, Alembic (миграции)
- **Брокер сообщений:** Kafka, FastStream
- **Валидация:** Pydantic

## Структура проекта
```text
gateway/
├── alembic/               # Инфраструктура для миграций базы данных
│   ├── versions/          # Сгенерированные файлы миграций
│   ├── env.py
│   ├── README
│   └── script.py.mako
├── app/                   # Основной код приложения
│   ├── __init__.py
│   ├── api.py             # HTTP роутеры (FastAPI)
│   ├── broker.py          # Инициализация и настройка Kafka-брокера
│   ├── config.py          # Настройки приложения и переменные окружения
│   ├── database.py        # Подключение к PostgreSQL и управление сессиями
│   ├── kafka_handlers.py  # Обработчики входящих сообщений из Kafka
│   ├── main.py            # Точка входа, сборка приложения
│   ├── models.py          # Декларативные модели SQLAlchemy
│   └── schemas.py         # Pydantic-схемы для валидации данных
├── tests/                 # Автотесты (pytest)
│   ├── conftest.py        # Общие фикстуры
│   ├── subscriber_test.py
│   ├── test_api.py
│   └── test_schemas.py
├── alembic.ini            # Главный конфигурационный файл Alembic
├── docker-compose.yml     # Конфигурация для запуска инфраструктуры
└── Dockerfile             # Инструкции для сборки Docker-образа
```

## Конфигурация
Для запуска проекта необходимо создать файл `.env` в корневой директории.
Пример переменных (значения по умолчанию из `config.py`):
```env
POSTGRES_USER=admin
POSTGRES_PASSWORD=root
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_DB=smartbank
KAFKA_HOST=localhost:9092
```

## Запуск приложения

### Запуск через Docker Compose (Рекомендуемый)
Позволяет поднять микросервис в единой сети со всей необходимой инфраструктурой (PostgreSQL, Kafka).

Сборка и запуск контейнеров (флаг `-d` запустит их в фоновом режиме):
```bash
docker-compose up --build -d
```

Остановка контейнеров:
```bash
docker-compose down
```

### Локальный запуск (через Uvicorn)
Из корня проекта выполните команду:
```bash
uvicorn app.main:app --reload
```

## Запуск тестов
В проекте настроены тесты для API, брокера и схем валидации (используется `pytest`).

Запустить все тесты можно командой:
```bash
pytest
```

Если нужно запустить тесты внутри уже запущенного Docker-контейнера шлюза (замените `gateway-app` на актуальное имя вашего контейнера):
```bash
docker exec -it gateway-app pytest
```

## API Endpoints

### `POST /ask`
Создает новую задачу на обработку запроса.

**Тело запроса:**
```json
{
  "query": "How transfer money to IP without fee"
}
```

**Успешный ответ (200 OK):**
```json
{
  "task_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "PENDING"
}
```

### `GET /status/{task_id}`
Проверяет статус выполнения задачи.

**Успешный ответ, задача в процессе (200 OK):**
```json
{
  "task_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "PENDING",
  "result": null
}
```

**Успешный ответ, задача выполнена (200 OK):**
```json
{
  "task_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "COMPLETED",
  "result": "{\"data\": \"Перевод без комиссии возможен через СБП...\"}"
}
```

**Ошибка, задача не найдена (404 Not Found):**
```json
{
  "detail": "Not found"
}
```
