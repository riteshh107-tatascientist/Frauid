"""
Health check and system status endpoints.
"""

import logging
from fastapi import APIRouter
from app.core.database import check_database_connection

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    System health check endpoint.
    
    Returns:
        Status of application, database, and model
    """
    db_connected = await check_database_connection()
    
    return {
        "status": "healthy" if db_connected else "degraded",
        "database": "connected" if db_connected else "disconnected",
        "model": "loaded",  # Will be updated in Phase 3
        "environment": "development"
    }


@router.get("/ready")
async def readiness_check():
    """
    Readiness probe for Kubernetes/container orchestration.
    
    Returns:
        200 if ready, 503 if not ready
    """
    db_connected = await check_database_connection()
    
    if db_connected:
        return {"ready": True}
    else:
        return {"ready": False}
