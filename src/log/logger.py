"""A module for logging configuration."""

import logging
import sys
from typing import Dict, Optional

_OTLP_HANDLERS: Dict[str, logging.Handler] = {}


def get_logger() -> logging.Logger:
    """Get an existing logger by service name.

    If the logger doesn't exist, it will be created with default settings.

    Args:
        service_name: Name of the service

    Returns:
        Logger instance

    Example:
        >>> logger = get_logger("api_gateway")
        >>> logger.info("Processing request")
    """
    from log.config import log_settings

    logger = logging.getLogger(log_settings.service_name)
    if not logger.handlers:
        # Logger not set up yet, initialize it with defaults
        return setup_logging(
            log_settings.service_name,
            log_settings.log_console_level,
            log_settings.log_otlp_level,
            log_settings.otlp_endpoint,
        )

    return logger


def handle_external_dep_logger(name: str, level: str = "WARNING"):
    """Configure external dependency logger to use the same handlers as our application logger.

    Args:
        name: Name of the external logger
        level: Log level for the external logger
    """
    logger = get_logger()
    external_logger = logging.getLogger(name)
    external_logger.setLevel(getattr(logging, level.upper(), logging.WARNING))
    external_logger.handlers = logger.handlers


def setup_logging(
    service_name: str,
    console_level: str = "DEBUG",
    otlp_level: str = "INFO",
    otlp_endpoint: Optional[str] = None,
) -> logging.Logger:
    """Set up logging for a microservice.

    This configures:
    - Colored console output for development
    - JSON output for otlp logging
    - OpenTelemetry trace context (trace_id and span_id) in all logs

    Args:
        service_name: Name of the service (e.g., "api_gateway")
        console_level: Log level for console output (default: DEBUG)
        otlp_level: Log level for otlp output (default: INFO)
        otlp_endpoint: Otlp collector endpoint URL. If None it does not enable otlp logging.

    Returns:
        Configured logger instance

    Example:
        >>> logger = setup_logging("api_gateway")
        >>> logger.info("Service started", extra={"port": 8000})
    """
    # Get or create logger
    logger = logging.getLogger(service_name)
    logger.setLevel(logging.DEBUG)

    # Clear any existing handlers to avoid duplicates
    logger.handlers.clear()

    # --- Console Handler ---
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, console_level.upper(), logging.DEBUG))

    # --- Console Formatter (Colored) ---
    from .formatters import ColoredConsoleFormatter

    console_formatter = ColoredConsoleFormatter(datefmt="%Y-%m-%d %H:%M:%S")
    console_handler.setFormatter(console_formatter)

    # --- Add OpenTelemetry Trace Filter ---
    # This automatically injects trace_id and span_id into every log
    from .filters import OTelTraceFilter

    otel_filter = OTelTraceFilter()
    console_handler.addFilter(otel_filter)

    # --- Attach Handlers ---
    logger.addHandler(console_handler)

    # --- OTLP Handler (sends logs to collector) ---
    if otlp_endpoint:
        try:
            otlp_handler = _get_otlp_logging_handler(service_name, otlp_level, otlp_endpoint)
            if otlp_handler:
                otlp_handler.addFilter(otel_filter)
                logger.addHandler(otlp_handler)
        except Exception as e:
            logger.exception("Failed to create OTLP logging handler", extra={"error": str(e)})

    else:
        logger.warning("OTLP endpoint not provided, skipping OTLP log handler setup.")

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


def _get_otlp_logging_handler(
    service_name: str, level: str, otlp_endpoint: str
) -> Optional[logging.Handler]:
    """Lazily build a LoggingHandler that forwards Python logs to the OTLP collector."""
    if service_name in _OTLP_HANDLERS:
        return _OTLP_HANDLERS[service_name]

    try:
        from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
        from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
        from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
        from opentelemetry.sdk.resources import Resource
    except ImportError:
        return None

    endpoint = otlp_endpoint.rstrip("/")
    exporter = OTLPLogExporter(endpoint=f"{endpoint}/v1/logs")
    provider = LoggerProvider(resource=Resource.create({"service.name": service_name}))
    provider.add_log_record_processor(BatchLogRecordProcessor(exporter))

    log_levels: Dict[str, int] = {
        "CRITICAL": logging.CRITICAL,
        "ERROR": logging.ERROR,
        "WARNING": logging.WARNING,
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
    }

    level_final = log_levels.get(level.upper(), logging.NOTSET)

    handler = LoggingHandler(level=level_final, logger_provider=provider)
    _OTLP_HANDLERS[service_name] = handler
    return handler
