"""Logging configuration settings."""

from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class LogSettings(BaseSettings):
    """Logging configuration settings for the application."""

    console_level: str = "DEBUG"
    otlp_level: str = "INFO"
    otlp_endpoint: Optional[str] = None
    model_config = SettingsConfigDict(
        env_prefix="LOG_",
        env_file=".env",
        extra="ignore",
        hide_input_in_errors=True,
    )


log_settings = LogSettings()
