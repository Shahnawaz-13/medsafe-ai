# app/routers/health.py
from fastapi import APIRouter
from datetime import datetime
import sys

router = APIRouter()


@router.get("/health")
async def health_check():
    """Service health check endpoint."""
    return {
        "status":      "ok",
        "service":     "MedSafe AI API",
        "version":     "1.0.0",
        "timestamp":   datetime.utcnow().isoformat() + "Z",
        "python":      sys.version,
        "environment": "development",
    }