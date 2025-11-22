"""An api to check the health of the service."""

from enum import Enum

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthCheckStatus(str, Enum):
    """Health check status values."""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"


class HealthCheckResponseModel(BaseModel):
    """Health check response model."""

    status: HealthCheckStatus


@router.get("/health")
async def health_check():
    """Health check endpoint to verify service is running."""
    return HealthCheckResponseModel(status=HealthCheckStatus.HEALTHY)
