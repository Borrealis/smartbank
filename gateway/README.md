# SmartBank Gateway

Gateway — HTTP-точка входа проекта. Он принимает вопрос пользователя, создаёт задачу в PostgreSQL, публикует её в Kafka и отдаёт готовый результат через polling API.

## Ответственность Gateway

1. Принимает вопрос через `POST /ask`.
2. Создаёт запись в таблице `tasks` со статусом `PENDING`.
3. Публикует сообщение в Kafka-топик `gateway-request`.
4. Слушает топик `worker-response`.
5. Обновляет задачу до `COMPLETED` или `FAILED` и сохраняет результат Worker.

## Поток сообщений

```text
POST /ask
  │
  ├── PostgreSQL: PENDING
  └── Kafka: gateway-request
                     │
                     ▼
                  Worker
                     │
                     ▼
              Kafka: worker-response
                     │
                     ▼
          Gateway subscriber → PostgreSQL
```

Топики используются в единственном числе:

| Топик | Направление |
| --- | --- |
| `gateway-request` | Gateway → Worker |
| `worker-response` | Worker → Gateway |

## HTTP API

### `POST /ask`

Создаёт асинхронную задачу.

Запрос:

```json
{
  "query": "Какие ограничения действуют при переводе денег?"
}
```

Поле `task_id` можно передать явно, но обычно Gateway создаёт UUID сам.

Успешный ответ:

```json
{
  "task_id": "<uuid>",
  "status": "PENDING"
}
```

### `GET /status/{task_id}`

Возвращает актуальное состояние задачи.

Пример результата после обработки:

```json
{
  "task_id": "<uuid>",
  "status": "COMPLETED",
  "result": {
    "answer": "...",
    "sources": ["docs/tariff.md"],
    "confidence": null
  }
}
```

Если задача не найдена, API возвращает `404`. Если Gateway не сохранил задачу или не отправил её в Kafka — `503`.

### `GET /health`

Проверяет доступность Kafka для Gateway.

## Конфигурация

Для локального запуска без Docker используется `gateway/.env`:

```env
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_SERVER=localhost
POSTGRES_PORT=5433
POSTGRES_DB=smartbank
KAFKA_HOST=localhost:9092
```

В Docker Compose адреса сервисов задаются явно: PostgreSQL — `db:5432`, Kafka — `kafka:29092`. Секреты передаются из корневого `.env`.

## Локальная разработка

Из папки `gateway`:

```bash
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

## Миграции

Из папки `gateway`:

```bash
uv run alembic revision --autogenerate -m "describe_change"
uv run alembic upgrade head
```

Перед применением всегда проверь созданную миграцию: autogenerate может увидеть лишние изменения схемы.

## Тесты

Из папки `gateway`:

```bash
uv run pytest -v
```

Тесты покрывают HTTP API, Kafka publisher/subscriber и Pydantic-схемы.
