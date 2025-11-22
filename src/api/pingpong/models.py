"""Pydantic models for Ping/Pong interaction."""

from pydantic import BaseModel, Field


class PingRequest(BaseModel):
    """Request model for Ping message."""

    message: str = Field(..., description="The message to send (should be 'Ping')")


class PongResponse(BaseModel):
    """Response model for Pong message."""

    message: str = Field(..., description="The response message (will be 'Pong')")


class SendPingRequest(BaseModel):
    """Request model for sending Ping to another service."""

    url: str = Field(..., description="The target service URL to send Ping to")
    message: str = Field(default="Ping", description="The message to send (default: 'Ping')")


class SendPingResponse(BaseModel):
    """Response model for send Ping operation."""

    success: bool = Field(..., description="Whether the Ping was successfully sent")
    response_message: str | None = Field(
        None, description="The response message from the target service"
    )
