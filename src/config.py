"""Configuration settings for the application."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):  # noqa: D101
    port: int = 3000
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        hide_input_in_errors=True,
    )


settings = Settings()
