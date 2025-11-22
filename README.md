# Python Microservice Template

A production-ready Python microservice template built with FastAPI, featuring distributed tracing, structured logging, and observability best practices. This template is designed to help you learn modern microservice patterns while providing a solid foundation for production deployments.

## What You'll Learn

This template demonstrates:

- **Distributed Tracing**: How to instrument your application with OpenTelemetry to track requests across services
- **Structured Logging**: JSON-formatted logs with automatic trace context injection for easy aggregation and analysis
- **Observability**: Integration with Prometheus metrics and OTLP exporters for comprehensive monitoring
- **Configuration Management**: Type-safe configuration using Pydantic Settings with environment variables
- **Middleware Patterns**: Request/response logging and trace propagation
- **API Design**: RESTful endpoints with proper validation and error handling

## Tech Stack

- **FastAPI** - Modern, fast web framework for building APIs
- **OpenTelemetry** - Vendor-neutral observability framework for tracing and metrics
- **Prometheus** - Metrics collection exposed at `/metrics` endpoint
- **Pydantic Settings** - Type-safe configuration management
- **httpx** - Modern HTTP client with async support and automatic trace propagation
- **Ruff** - Fast Python linter and formatter (configured for Google-style docstrings)
- **Poetry** - Dependency management

## Quick Start

### 1. Initialize Workspace

```bash
python init-ws.py
```

This script automates the setup:

- Creates a Python virtual environment
- Installs Poetry inside the virtual environment
- Installs all dependencies
- Sets up pre-commit hooks for code quality
- Installs recommended VSCode extensions

### 2. Run the Service

```bash
# Activate the virtual environment (if not already activated)
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Run the service
python src/main.py
```

The service starts on port 3000 by default. Access:

- API docs: http://localhost:3000/docs
- Metrics: http://localhost:3000/metrics
- Health check: http://localhost:3000/api/v1/health

### 3. Try the Ping/Pong Example

The template includes a simple inter-service communication example:

```bash
# Send a ping to another service instance
curl -X POST http://localhost:3000/api/v1/ping \
  -H "Content-Type: application/json" \
  -d '{"url": "http://localhost:3001"}'

# Or receive a ping (when called by another instance)
curl -X POST http://localhost:3000/api/v1/pong \
  -H "Content-Type: application/json" \
  -d '{"message": "Ping"}'
```

## Key Concepts

### Structured Logging

All logs are output as JSON lines with automatic trace context, formatters manage the visualization on the console:

```python
from log import get_logger

logger = get_logger()
logger.info("Processing request", extra={"user_id": 123, "action": "create"})
```

Output:

```json
{
  "timestamp": "2025-11-22T18:00:00",
  "level": "INFO",
  "message": "Processing request",
  "user_id": 123,
  "action": "create",
  "trace_id": "abc123",
  "span_id": "def456"
}
```

### Distributed Tracing

The template automatically instruments FastAPI and httpx with OpenTelemetry:

- **Incoming requests** create root spans
- **Outgoing HTTP calls** propagate trace context (W3C Trace Context headers)
- **Trace IDs** flow through the entire request chain across services

Configure the OTLP endpoint to send traces to your collector:

```bash
export OTLP_ENDPOINT=http://localhost:4318  # OTEL Collector HTTP endpoint
```

### Configuration

Environment-based configuration with type safety:

```python
# src/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    service_name: str = "microservice"
    port: int = 3000
    otlp_endpoint: str | None = None

    class Config:
        env_file = ".env"
```

Create a `.env` file:

```bash
SERVICE_NAME=my-service
PORT=8000
OTLP_ENDPOINT=http://localhost:4318
```

### Telemetry Setup

The `telemetry.py` module encapsulates all instrumentation:

```python
from telemetry import setup_instrumentation, shutdown_instrumentation

# In main.py
setup_instrumentation(app, settings.service_name, settings.otlp_endpoint)
```

This sets up:

- OpenTelemetry tracer provider with OTLP exporter
- FastAPI automatic instrumentation (creates spans for all requests)
- httpx automatic instrumentation (propagates trace context)
- Prometheus metrics at `/metrics`

## Development Commands

### Dependencies

```bash
# Add a new dependency
poetry add package-name

# Add a dev dependency
poetry add --group dev package-name

# Update dependencies
poetry update
```

## Project Structure

```
src/
  api/                  # API routes organized by domain
    health.py           # Health check endpoint
    pingpong/           # Example: inter-service communication
      __init__.py
      models.py
      routes.py
  log/                  # Logging infrastructure
    logger.py           # Logger setup and configuration
    config.py           # Logging-specific settings
    filters/            # Custom log filters (trace context injection)
    formatters/         # Custom formatters (JSON line format)
  middleware/           # Custom middleware
    log_mw.py           # Request/response logging
  utils/                # Shared utilities
    tracing.py          # Trace context helpers
    constants.py        # Application constants
  config.py             # Application settings
  telemetry.py          # OpenTelemetry and Prometheus setup
  main.py               # Application entry point
```

## Environment Variables

| Variable            | Description                          | Default           |
| ------------------- | ------------------------------------ | ----------------- |
| `SERVICE_NAME`      | Name of the service (used in traces) | `microservice`    |
| `PORT`              | Port to run the service on           | `3000`            |
| `OTLP_ENDPOINT`     | OpenTelemetry collector endpoint     | `None` (disabled) |
| `LOG_NAME`          | Logger name                          | `app`             |
| `LOG_CONSOLE_LEVEL` | Console log level                    | `DEBUG`           |
| `LOG_OTLP_LEVEL`    | OTLP log level                       | `INFO`            |
| `LOG_OTLP_ENDPOINT` | OTLP endpoint for logs               | `None` (disabled) |

## Next Steps

1. **Explore the `/docs`**: FastAPI auto-generates interactive API documentation
2. **Add Your Routes**: Create new routers in `src/api/` following the `pingpong` example
3. **Configure Observability**: Set up an OTEL Collector and connect Jaeger/Tempo for traces
4. **Add Tests**: Write tests in `tests/` using pytest fixtures
5. **Customize**: Modify `config.py` and `telemetry.py` for your needs

## Learn More

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenTelemetry Python](https://opentelemetry.io/docs/languages/python/)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [Structured Logging Best Practices](https://www.structlog.org/en/stable/why.html)

## License

MIT
