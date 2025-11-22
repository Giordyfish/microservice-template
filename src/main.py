"""Application entry point."""

import uvicorn
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager

from api.health import router as health_router
from api.pingpong import router as pingpong_router
from config import settings
from log import get_logger, handle_external_dep_logger
from middleware import LogMiddleware
from telemetry import setup_instrumentation, shutdown_instrumentation
from utils.constants import APP_API_V1_PREFIX, APP_DESCRIPTION, APP_VERSION

logger = get_logger()
handle_external_dep_logger("uvicorn.error")
handle_external_dep_logger("opentelemetry.attributes")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the FastAPI application.

    Runs startup and shutdown logic.
    """
    # Startup
    logger.info(
        "API Gateway starting up",
        extra={
            "otel_endpoint": settings.otlp_endpoint,
        },
    )
    yield
    # Shutdown
    logger.info("API Gateway shutting down")
    shutdown_instrumentation()


app = FastAPI(
    title=settings.service_name.capitalize(),
    version=APP_VERSION,
    description=APP_DESCRIPTION,
    lifespan=lifespan,
)

# Setup OpenTelemetry and Prometheus instrumentation
setup_instrumentation(app, settings.service_name, settings.otlp_endpoint)

# Add LogMiddleware
app.add_middleware(
    LogMiddleware,  # ty: ignore
)

app.include_router(health_router, tags=["Health"], prefix=APP_API_V1_PREFIX)
app.include_router(pingpong_router, tags=["Ping/Pong"], prefix=APP_API_V1_PREFIX)

if __name__ == "__main__":
    try:
        logger.info("Starting application on port", extra={"port": settings.port})
        uvicorn.run(app, host="0.0.0.0", log_config=None, port=settings.port)

    except Exception as e:
        logger.exception("Error starting API", extra={"error": str(e)})
