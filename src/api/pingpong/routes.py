"""API routes for Ping/Pong interaction between microservices."""

import httpx
from fastapi import APIRouter

from api.pingpong.models import (
    PingRequest,
    PongResponse,
    SendPingRequest,
    SendPingResponse,
)
from log import get_logger

logger = get_logger()
router = APIRouter()


@router.post("/ping", response_model=SendPingResponse)
async def ping(request: SendPingRequest):
    """Send a Ping message to another service.

    This endpoint sends a POST request with message "Ping" to the specified
    URL and returns the response. The target service should respond with "Pong".

    Args:
        request: The send ping request containing the target URL

    Returns:
        SendPingResponse with success status and response message or error

    Example:
        >>> # POST /ping with body: {"url": "http://localhost:8000", "message": "Ping"}
        >>> # Response: {"success": true, "response_message": "Pong", "error": null}
    """
    logger.info(
        "Sending ping to remote service",
        extra={"url": request.url, "ping_message": request.message},
    )

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            from utils.constants import APP_API_V1_PREFIX

            response = await client.post(
                request.url.rstrip("/") + APP_API_V1_PREFIX + "/pong",
                json={"message": request.message},
                headers={"Content-Type": "application/json"},
            )

            # Check if request was successful
            response.raise_for_status()

            # Parse response
            response_data = response.json()
            response_message = response_data.get("message")

            logger.info(
                "Received response from remote service",
                extra={
                    "url": request.url,
                    "status_code": response.status_code,
                    "response_message": response_message,
                },
            )

            if response_message != "Pong":
                logger.warning(
                    "Unexpected response message from remote service",
                    extra={"url": request.url, "response_message": response_message},
                )
                return SendPingResponse(
                    success=False,
                    response_message=response_message,
                )

            return SendPingResponse(success=True, response_message=response_message)

    except httpx.HTTPStatusError as e:
        logger.error(
            "HTTP error when sending ping",
            extra={"url": request.url, "status_code": e.response.status_code, "error": str(e)},
        )
        return SendPingResponse(
            success=False,
            response_message=None,
        )

    except httpx.RequestError as e:
        logger.error(
            "Request error when sending ping",
            extra={"url": request.url, "error": str(e)},
        )
        return SendPingResponse(success=False, response_message=None)

    except Exception as e:
        logger.exception(
            "Unexpected error when sending ping",
            extra={"url": request.url, "error": str(e)},
        )
        return SendPingResponse(success=False, response_message=None)


@router.post("/pong", response_model=PongResponse)
async def pong(request: PingRequest):
    """Receive a Ping message and respond with Pong.

    This endpoint validates that the incoming message is "Ping" (case insensitive)
    and responds with "Pong". If the message is not "Ping", it returns an error.

    Args:
        request: The ping request containing the message

    Returns:
        PongResponse with message "Pong"

    Raises:
        HTTPException: 400 if the message is not "Ping"

    Example:
        >>> # POST /pong with body: {"message": "Ping"}
        >>> # Response: {"message": "Pong"}
    """
    logger.info("Received ping request", extra={"ping_message": request.message})

    if request.message.strip().lower() != "ping":
        logger.warning(
            "Invalid ping message received",
            extra={"expected": "Ping", "received_message": request.message},
        )
        return PongResponse(message='Message must be "Ping" to receive "Pong" response')

    logger.info("Responding with Pong")
    return PongResponse(message="Pong")
