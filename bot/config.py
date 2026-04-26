import logging
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    bot_token: str = Field(..., alias="BOT_TOKEN")
    database_path: Path = Field(default=Path("data/reminders.db"), alias="DATABASE_PATH")
    timezone: str = Field(default="Europe/Moscow", alias="TIMEZONE")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    scheduler_interval: int = Field(default=60, alias="SCHEDULER_INTERVAL")

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, value: str) -> str:
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper = value.upper()
        if upper not in allowed:
            raise ValueError(f"Недопустимый уровень логирования: {value}. Допустимые: {allowed}")
        return upper

    @field_validator("scheduler_interval")
    @classmethod
    def validate_interval(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("Интервал планировщика должен быть больше 0")
        return value

    @property
    def log_level_int(self) -> int:
        return getattr(logging, self.log_level)


def get_settings() -> Settings:
    return Settings()
