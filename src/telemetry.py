"""OpenTelemetry and Prometheus instrumentation setup."""

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from prometheus_fastapi_instrumentator import Instrumentator

from log import get_logger

logger = get_logger()


def setup_instrumentation(app: FastAPI, service_name: str, otlp_endpoint: str | None = None):
    """Set up OpenTelemetry and Prometheus instrumentation for FastAPI app.

    Args:
        app: The FastAPI application instance
        service_name: Name of the service for OpenTelemetry resource
        otlp_endpoint: Optional OTLP collector endpoint for trace export
    """
    # Initialize OpenTelemetry
    resource = Resource.create({"service.name": service_name})
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)

    # Configure OTLP exporter to send traces to Tempo via OTEL Collector
    if otlp_endpoint:
        logger.info(
            "Configuring OTLP exporter for OpenTelemetry",
            extra={"otlp_endpoint": otlp_endpoint},
        )
        otlp_exporter = OTLPSpanExporter(endpoint=f"{otlp_endpoint}/v1/traces")
        span_processor = BatchSpanProcessor(otlp_exporter)
        tracer_provider.add_span_processor(span_processor)
    else:
        logger.warning("OTLP endpoint not provided, skipping OTLP trace exporter setup.")

    # Instrument FastAPI with OpenTelemetry
    # This automatically creates spans for all HTTP requests
    FastAPIInstrumentor.instrument_app(app)

    # Instrument httpx client for automatic trace propagation to downstream services
    HTTPXClientInstrumentor().instrument()

    # Expose default Prometheus metrics at /metrics
    Instrumentator().instrument(app).expose(app, include_in_schema=False)

    logger.info("Instrumentation setup completed")


def shutdown_instrumentation():
    """Shutdown instrumentation and flush remaining traces."""
    tracer_provider = trace.get_tracer_provider()
    if isinstance(tracer_provider, TracerProvider):
        tracer_provider.force_flush()
        logger.info("Traces flushed successfully")
