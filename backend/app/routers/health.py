# app/routers/health.py
from fastapi import APIRouter
from datetime import datetime
import sys
from app.services.cache_service import get_cache_stats
from app.database import get_db

router = APIRouter()


@router.get("/health")
async def health_check():
    """Full service health check."""
    db        = get_db()
    db_status = "connected" if db is not None else "disconnected"

    cache_stats = await get_cache_stats()

    from app.config import settings
    groq_configured = bool(settings.groq_api_key)

    return {
        "status":    "ok",
        "service":   "MedSafe AI API",
        "version":   "1.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "python":    sys.version.split()[0],
        "components": {
            "database":   db_status,
            "ai_provider": "groq",
            "ai_status":  (
                "configured" if groq_configured
                else "not configured"
            ),
            "cache":      cache_stats,
        }
    }


@router.get("/health/simple")
async def health_simple():
    """Lightweight uptime check."""
    return {"status": "ok"}


@router.get("/health/ai")
async def health_ai():
    """Test Groq AI connectivity."""
    from app.services.claude_service import test_claude_connection
    result = await test_claude_connection()
    return result