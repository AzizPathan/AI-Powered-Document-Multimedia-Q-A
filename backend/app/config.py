from functools import lru_cache
from os import getenv
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")

    database_url: str = "sqlite+pysqlite:///./dev.db"
    redis_url: str | None = None
    openai_api_key: str | None = None
    jwt_secret: str = "dev-secret"
    jwt_algorithm: str = "HS256"
    upload_dir: Path = Path("uploads")
    backend_cors_origins: str = "http://localhost:5173"
    rate_limit_per_minute: int = 60

    @property
    def cors_origins(self) -> list[str]:
        return [item.strip() for item in self.backend_cors_origins.split(",") if item.strip()]

    @property
    def resolved_database_url(self) -> str:
        docker_database = "@db:5432/" in self.database_url
        if docker_database and not Path("/.dockerenv").exists():
            return "sqlite+pysqlite:///./dev.db"
        if getenv("VERCEL") and self.database_url.startswith("sqlite"):
            return "sqlite+pysqlite:////tmp/dev.db"
        return self.database_url

    @property
    def resolved_upload_dir(self) -> Path:
        upload_dir = self.upload_dir
        if getenv("VERCEL") and not upload_dir.is_absolute():
            return Path("/tmp/uploads")
        is_docker_default = upload_dir.as_posix() == "/app/uploads"
        if is_docker_default and not Path("/.dockerenv").exists():
            return Path("../runtime/uploads")
        return upload_dir


@lru_cache
def get_settings() -> Settings:
    return Settings()
