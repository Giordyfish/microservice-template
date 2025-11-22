"""Application entry point."""

import logging

import uvicorn
from fastapi import FastAPI

from api.health import router as health_router
from config import settings
from log import get_logger
from middleware import LogMiddleware
from utils.constants import APP_API_V1_PREFIX, APP_DESCRIPTION, APP_NAME, APP_VERSION

logger = get_logger()

# Configure uvicorn loggers to use the same handlers as our application logger
uvicorn_error_logger = logging.getLogger("uvicorn.error")
uvicorn_error_logger.setLevel(logging.INFO)
uvicorn_error_logger.handlers = logger.handlers

# Configure opentelemetry loggers to use the same handlers as our application logger
opentelemetry_attributes_logger = logging.getLogger("opentelemetry.attributes")
opentelemetry_attributes_logger.setLevel(logging.WARNING)
opentelemetry_attributes_logger.handlers = logger.handlers

app = FastAPI(title=APP_NAME.capitalize(), version=APP_VERSION, description=APP_DESCRIPTION)

# Add LogMiddleware
app.add_middleware(
    LogMiddleware,  # ty: ignore
)

app.include_router(health_router, tags=["Health"], prefix=APP_API_V1_PREFIX)

if __name__ == "__main__":
    try:
        logger.info("Starting application on port", extra={"port": settings.port})
        uvicorn.run(app, host="0.0.0.0", log_config=None, port=settings.port)

    except Exception as e:
        logger.exception("Error starting API", extra={"error": str(e)})
