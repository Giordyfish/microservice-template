"""Application entry point."""

import logging

import uvicorn
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager

# OpenTelemetry imports
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from prometheus_fastapi_instrumentator import Instrumentator

from api.health import router as health_router
from api.pingpong import router as pingpong_router
from config import settings
from log import get_logger
from middleware import LogMiddleware
from utils.constants import APP_API_V1_PREFIX, APP_DESCRIPTION, APP_VERSION

logger = get_logger()

# Configure uvicorn loggers to use the same handlers as our application logger
uvicorn_error_logger = logging.getLogger("uvicorn.error")
uvicorn_error_logger.setLevel(logging.WARNING)
uvicorn_error_logger.handlers = logger.handlers

# Configure opentelemetry loggers to use the same handlers as our application logger
opentelemetry_attributes_logger = logging.getLogger("opentelemetry.attributes")
opentelemetry_attributes_logger.setLevel(logging.WARNING)
opentelemetry_attributes_logger.handlers = logger.handlers

# Initialize OpenTelemetry
resource = Resource.create({"service.name": settings.service_name})
tracer_provider = TracerProvider(resource=resource)
trace.set_tracer_provider(tracer_provider)

# Configure OTLP exporter to send traces to Tempo via OTEL Collector
if settings.otlp_endpoint:
    logger.info(
        "Configuring OTLP exporter for OpenTelemetry",
        extra={"otlp_endpoint": settings.otlp_endpoint},
    )
    otlp_exporter = OTLPSpanExporter(endpoint=f"{settings.otlp_endpoint}/v1/traces")
    span_processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(span_processor)
else:
    logger.warning("OTLP endpoint not provided, skipping OTLP trace exporter setup.")


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
    # Ensure all spans are exported before shutdown
    tracer_provider.force_flush()


app = FastAPI(
    title=settings.service_name.capitalize(),
    version=APP_VERSION,
    description=APP_DESCRIPTION,
    lifespan=lifespan,
)

# Instrument FastAPI with OpenTelemetry
# This automatically creates spans for all HTTP requests
FastAPIInstrumentor.instrument_app(app)

# Instrument httpx client for automatic trace propagation to downstream services
HTTPXClientInstrumentor().instrument()

# Expose default Prometheus metrics at /metrics
Instrumentator().instrument(app).expose(app, include_in_schema=False)

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
