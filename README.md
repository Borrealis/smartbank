# SmartBank Compliance & Product RAG Agent

Асинхронный банковский помощник. Gateway принимает вопрос, сохраняет задачу и отправляет её в Kafka. Worker выполняет RAG-поиск по внутренним документам, при необходимости получает тариф клиента и возвращает результат.

## Архитектура

```text
Client
  │ POST /ask
  ▼
Gateway (FastAPI) ──► PostgreSQL: task = PENDING
  │
  ▼ gateway-request
Kafka
  │
  ▼
Worker (FastStream + RAG) ──► pgvector + LLM tools
  │
  ▼ worker-response
Kafka ──► Gateway ──► PostgreSQL: COMPLETED / FAILED
```

| Компонент | Назначение |
| --- | --- |
| `gateway/` | HTTP API, задачи в БД, Kafka publisher/subscriber |
| `worker/` | Kafka consumer, ReAct-цикл, RAG и ingestion |
| `docs/` | Исходные Markdown-документы для базы знаний |
| PostgreSQL + pgvector | Задачи, документы, чанки и embeddings размерности 1536 |
| Kafka | Асинхронный обмен между Gateway и Worker |

## Быстрый запуск через Docker

### 1. Создать корневой `.env`

В корне проекта создай `.env`. Для Docker Compose в нём нужны как минимум:

```env
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
GEMINI_API_KEY=your_gemini_api_key
```

Не коммить этот файл: в нём секреты.

### 2. Поднять проект

```bash
make run
```

Команда запускает Gateway, Worker, PostgreSQL, Kafka и Kafka UI. Логи останутся в текущем терминале; остановка — `Ctrl+C`.

Сервисы доступны по адресам:

| Сервис | Адрес |
| --- | --- |
| Gateway API | `http://localhost:8000` |
| Kafka UI | `http://localhost:8080` |
| PostgreSQL с хоста | `localhost:5433` |

### 3. Загрузить документы в pgvector

После запуска контейнеров подготовь `worker/.env` для локального ingestion: в нём нужен `GEMINI_API_KEY` и параметры подключения к PostgreSQL с хоста (`POSTGRES_SERVER=localhost`, `POSTGRES_PORT=5433`, `POSTGRES_DB=smartbank`).

Затем из корня проекта выполни:

```bash
make ingest
```

Команда читает `docs/compliance.md` и `docs/tariff.md`, разбивает текст на чанки, создаёт embeddings и записывает их в PostgreSQL.

## Проверка API

Отправить вопрос:

```bash
curl -s -X POST http://localhost:8000/ask \
  -H 'Content-Type: application/json' \
  -d '{"query":"Какие ограничения действуют при переводе денег?"}'
```

Ответ сразу вернёт `task_id` и статус `PENDING`.

Проверить результат:

```bash
curl -s http://localhost:8000/status/<task_id>
```

После обработки Worker вернёт `COMPLETED` с полями `answer`, `sources` и `confidence`, либо `FAILED`.

## Основные команды

```bash
make help       # список команд
make install    # синхронизировать зависимости
make build      # собрать Docker-образы
make run        # поднять весь проект
make ingest     # загрузить документы в pgvector
```

Подробности сервисов:

- [Gateway](gateway/README.md)
- [Worker](worker/README.md)
