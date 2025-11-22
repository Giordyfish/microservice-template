"""Logging configuration settings."""

from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class LogSettings(BaseSettings):
    """Logging configuration settings for the application."""

    service_name: str = "microservice"
    log_console_level: str = "DEBUG"
    log_otlp_level: str = "INFO"
    otlp_endpoint: Optional[str] = None
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        hide_input_in_errors=True,
    )


log_settings = LogSettings()
