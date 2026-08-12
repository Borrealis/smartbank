from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context

from gateway.app.models import Base
from gateway.app.config import settings

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_online() -> None:
    # Берем URL из конфига по пункту 4 и меняем драйвер для синхронного запуска Alembic
    sync_url = settings.database_url.replace(
        "postgresql+asyncpg", "postgresql+psycopg2"
    )
    connectable = create_engine(sync_url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
