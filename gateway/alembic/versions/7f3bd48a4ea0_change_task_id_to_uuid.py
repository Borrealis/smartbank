"""change_task_id_to_uuid

Revision ID: 7f3bd48a4ea0
Revises:
Create Date: 2026-08-13 00:08:48.100438

"""

from collections.abc import Sequence

import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

from alembic import op

# [01] Идентификаторы ревизии (версии схемы миграции)
revision: str = "7f3bd48a4ea0"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema (применение изменений схемы базы данных)."""
    # [02] Активируем расширение pgvector в PostgreSQL перед созданием векторных колонок
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # [03] Создание таблицы клиентов
    op.create_table(
        "clients",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=True),
        sa.Column("tariff_plan", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # [04] Создание таблицы документов (родительская таблица для чанков)
    op.create_table(
        "documents",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("product_category", sa.String(), nullable=True),
        sa.Column("source_url", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # [05] Создание таблицы асинхронных задач
    op.create_table(
        "tasks",
        sa.Column("task_id", sa.UUID(), nullable=False),
        sa.Column("query", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=True),
        sa.Column("result", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("task_id"),
    )

    # [06] Создание таблицы фрагментов документов с эмбеддингами
    op.create_table(
        "document_chunks",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("document_id", sa.String(), nullable=True),
        sa.Column("text_content", sa.Text(), nullable=True),
        sa.Column("embedding", Vector(1536), nullable=True),
        sa.Column("chunk_index", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["documents.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema (откат изменений схемы базы данных)."""
    # [07] Удаление таблиц в обратном порядке (сначала дочерние с внешними ключами)
    op.drop_table("document_chunks")
    op.drop_table("tasks")
    op.drop_table("documents")
    op.drop_table("clients")

    # [08] Отключение расширения pgvector при полном откате
    op.execute("DROP EXTENSION IF EXISTS vector;")
