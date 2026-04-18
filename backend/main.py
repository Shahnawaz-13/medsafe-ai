# main.py
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv

from app.config import settings
from app.database import connect_db, close_db
from app.middleware.rate_limit import limiter
from app.routers import (
    health, analyze, drug_info,
    chat, history, upload
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Lifespan (startup + shutdown) ────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 MedSafe AI API starting up...")
    await connect_db()
    logger.info("✅ All services ready")
    yield
    # Shutdown
    logger.info("Shutting down MedSafe AI API...")
    await close_db()
    logger.info("👋 Goodbye")


# ── FastAPI App ───────────────────────────────────────────────────────
app = FastAPI(
    title="MedSafe AI API",
    description=(
        "AI-powered drug interaction checker. "
        "Powered by OpenFDA, RxNorm, and Claude AI."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# ── Rate Limiter ──────────────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler
)


# ── CORS ──────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# ── Global Exception Handler ──────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception
):
    logger.error(
        f"Unhandled error on {request.url}: {exc}",
        exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content={
            "error":   "Internal server error",
            "message": "Something went wrong. Please try again.",
        },
    )


# ── Routers ───────────────────────────────────────────────────────────
app.include_router(health.router,   tags=["Health"])
app.include_router(analyze.router,  prefix="/api", tags=["Analysis"])
app.include_router(drug_info.router,prefix="/api", tags=["Drug Info"])
app.include_router(chat.router,     prefix="/api", tags=["Chat"])
app.include_router(history.router,  prefix="/api", tags=["History"])
app.include_router(upload.router,   prefix="/api", tags=["Upload"])


# ── Root ──────────────────────────────────────────────────────────────
@app.get("/")
async def root():
    return {
        "service": "MedSafe AI API",
        "version": "1.0.0",
        "status":  "running",
        "docs":    "/docs",
    }