from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables or .env."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="Digital Event Manager API")
    api_v1_prefix: str = Field(default="/api/v1")
    environment: str = Field(default="local")

    db_host: str = Field(default="db")
    db_port: int = Field(default=5432)
    db_user: str = Field(default="postgres")
    db_password: str = Field(default="postgres")
    db_name: str = Field(default="digital_events")
    db_echo: bool = Field(default=False)

    # Email confirmation
    email_confirmation_secret_key: str = Field(default="test-email-confirmation-secret")
    email_confirmation_time_window_minutes: int = Field(default=2)

    # SMTP configuration
    smtp_server: str = Field(default="smtp.yandex.ru", validation_alias="SMTP_SERVER")
    smtp_port: int = Field(default=587)
    email_login: str = Field(default="", validation_alias="EMAIL_LOGIN")
    email_password: str = Field(default="", validation_alias="EMAIL_PASSWORD")

    jwt_secret_key: str = Field(default="test-secret-key")
    jwt_ttl_minutes: int = Field(default=1440)

    # Comma-separated list of origins allowed to call the API from a browser.
    cors_origins: str = Field(default="http://localhost:5173,http://localhost:8080")

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def database_url(self) -> str:
        """Async connection string for SQLAlchemy."""
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def sync_database_url(self) -> str:
        """Sync connection string for Alembic."""
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
