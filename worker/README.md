# SmartBank Worker

Worker — фоновый Kafka-сервис. Он получает задачу от Gateway, запускает ReAct-цикл с tools, ищет данные в pgvector и возвращает готовый ответ.

## Ответственность Worker

1. Слушает Kafka-топик `gateway-request`.
2. Передаёт вопрос в `run_agentic_loop`.
3. Даёт LLM доступ к tools.
4. Публикует результат в `worker-response`.

При ошибке Worker не оставляет задачу в вечном ожидании: он публикует статус `FAILED`.

## RAG-пайплайн

```text
Kafka message
  ↓
LLM decides which tool to call
  ↓
search_compliance_knowledge
  ↓
Gemini embedding (1536 values)
  ↓
PostgreSQL + pgvector cosine distance
  ↓
Relevant chunks
  ↓
LLM final answer + source URLs
  ↓
Kafka: worker-response
```

## Tools

### `search_compliance_knowledge`

Принимает:

```text
search_query: str
product_category: str | None
```

Создаёт embedding запроса, ищет до трёх ближайших чанков по cosine distance и при необходимости фильтрует их по категории документа.

Возвращает текст чанков, название документа и `source_url`.

### `get_client_tariff_info`

Принимает `client_id` и читает mock-таблицу `clients`.

Всегда возвращает одинаковую структуру:

```json
{
  "client_id": "client_66",
  "tariff": "Premium",
  "status": "active",
  "error": null
}
```

Если клиента нет, `tariff` и `status` равны `null`, а `error` содержит причину.

## Документы и ingestion

Исходные документы лежат в корневой папке `docs/`:

- `docs/compliance.md`;
- `docs/tariff.md`.

Скрипт `worker/worker_scripts/ingest_docs.py`:

1. разбивает Markdown по заголовкам и затем на чанки размером 500 символов с overlap 50;
2. создаёт embedding каждого чанка через `gemini-embedding-001`;
3. сохраняет документы и чанки в таблицы `documents` и `document_chunks`.

Запускать ingestion нужно из корня репозитория:

```bash
make ingest
```

Для локального запуска скрипт читает `worker/.env`. В нём нужны `GEMINI_API_KEY` и host-параметры PostgreSQL, например `POSTGRES_SERVER=localhost`, `POSTGRES_PORT=5433`, `POSTGRES_DB=smartbank`.

## Конфигурация

Для запуска Worker локально создай `worker/.env`:

```env
GEMINI_API_KEY=your_gemini_api_key
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_SERVER=localhost
POSTGRES_PORT=5433
POSTGRES_DB=smartbank
KAFKA_HOST=localhost:9092
```

В Docker Compose Worker использует внутренние адреса `db:5432` и `kafka:29092`.

## Локальный запуск Worker

Из папки `worker`:

```bash
uv sync
uv run faststream run app.main:app
```

## Тесты

Тесты Worker не используют внешний embedding API. Они подменяют его функцией, которая возвращает вектор длиной 1536.

Векторные и tool-тесты используют отдельную БД `smartbank_test` с расширением `vector`.

Из папки `worker`:

```bash
POSTGRES_DB=smartbank_test uv run pytest -v
```

Перед первым запуском создай тестовую БД и расширение:

```bash
docker compose exec db psql -U <postgres_user> -d postgres -c "CREATE DATABASE smartbank_test;"
docker compose exec db psql -U <postgres_user> -d smartbank_test -c "CREATE EXTENSION vector;"
```
