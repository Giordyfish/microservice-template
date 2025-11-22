"""Middleware for logging HTTP requests and responses."""

import time

from starlette.middleware.base import BaseHTTPMiddleware

from log import get_logger


class LogMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses."""

    async def dispatch(self, request, call_next):
        """Log request and response details."""
        start_time = time.time()

        logger = get_logger()

        # Log incoming request
        logger.info(
            "HTTP request started",
            extra={
                "req_method": request.method,
                "req_url": str(request.url),
                "req_path": request.url.path,
                "req_query": str(request.url.query) if request.url.query else None,
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
            },
        )

        response = await call_next(request)

        # Calculate response time
        response_time_ms: float = round((time.time() - start_time) * 1000, 2)

        # Log response
        logger.info(
            "HTTP request completed",
            extra={
                "req_method": request.method,
                "req_path": request.url.path,
                "res_status_code": response.status_code,
                "response_time_ms": response_time_ms,
            },
        )

        return response
