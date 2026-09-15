from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

WORKER_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=WORKER_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    gemini_api_key: str = ""
    postgres_user: str = "admin"
    postgres_password: str = "root"
    postgres_server: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "smartbank"
    kafka_host: str = "localhost:9092"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_server}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
