"""
backend/app/main.py

FastAPI application entry point for the IROP Passenger Rebooking Copilot.

Responsibilities:
  - Create the FastAPI app instance.
  - Configure CORS (reads allowed origins from settings).
  - Register all API routers under /api/v1.
  - Expose /health for infrastructure health-checks.
  - Call configure_logging() on startup.

What does NOT live here:
  - No business logic.
  - No direct database access.
  - No AI / LangGraph code.
  - Individual router modules live in app/routers/.

Run locally:
    uvicorn app.main:app --reload --port 8000
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import configure_logging, get_logger

# ── Logger for this module ─────────────────────────────────────────────────
logger = get_logger(__name__)


# ── Lifespan (startup / shutdown) ─────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Executed once on startup and once on shutdown.
    Use for: DB connection pool warm-up, background task init, etc.
    """
    configure_logging(debug=settings.DEBUG)
    logger.info(
        "%s v%s starting up  [AI_REASONING=%s  DEBUG=%s]",
        settings.APP_NAME,
        settings.APP_VERSION,
        settings.USE_AI_REASONING,
        settings.DEBUG,
    )
    yield
    # ── Shutdown ────────────────────────────────────────────────
    logger.info("%s shutting down.", settings.APP_NAME)


# ── App instance ───────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "AI-assisted airline disruption management API. "
        "Employees cancel flights, the system scores every affected passenger, "
        "generates rebooking recommendations, and keeps a human in the loop."
    ),
    docs_url="/docs",          # Swagger UI
    redoc_url="/redoc",        # ReDoc UI
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


# ── CORS ───────────────────────────────────────────────────────────────────
# Origins are read from CORS_ORIGINS in .env — never use allow_origins=["*"]
# in a real deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],       # tighten in production
    allow_headers=["*"],       # tighten in production
)


# ── Health-check endpoint ──────────────────────────────────────────────────
@app.get(
    "/health",
    tags=["Health"],
    summary="Liveness probe",
    response_description="Service is reachable",
)
async def health_check() -> dict:
    """
    Returns 200 OK when the service is running.
    Used by Render/Railway health-check and the frontend during boot.
    """
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


# ── API routers ────────────────────────────────────────────────────────────
# Routers are registered here as they are built in later phases.
# Pattern:
#   from app.routers import auth, flights, passengers, ...
#   app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
#
# Phase 3 (Auth):
from app.routers.auth import router as auth_router

app.include_router(auth_router)  # exposes POST /auth/login directly
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)  # exposes POST /api/v1/auth/login
#
# Phase 4 (Flights & Bookings):
from app.routers import flights, passengers
app.include_router(flights.router, prefix=settings.API_V1_PREFIX, tags=["Flights"])
app.include_router(passengers.router, prefix=settings.API_V1_PREFIX, tags=["Passengers"])
# from app.routers import alternatives
# app.include_router(alternatives.router, prefix=settings.API_V1_PREFIX, tags=["Alternatives"])
#
# Phase 5 (Rebooking engine):
from app.routers import rebooking
app.include_router(rebooking.router, prefix=settings.API_V1_PREFIX, tags=["Rebooking"])
#
# Phase 6 (Notifications):
from app.routers import notifications
app.include_router(notifications.router, prefix=settings.API_V1_PREFIX, tags=["Notifications"])
#
# Phase 7 (CSV upload):
# from app.routers import uploads
# app.include_router(uploads.router, prefix=settings.API_V1_PREFIX, tags=["Uploads"])
#
# Phase 9 (Passenger portal):
from app.routers import portal
app.include_router(portal.router, prefix=settings.API_V1_PREFIX, tags=["Portal"])
#
# Dashboard:
from app.routers import dashboard
app.include_router(dashboard.router, prefix=settings.API_V1_PREFIX, tags=["Dashboard"])
#
# Dashboard aggregate:
# from app.routers import dashboard
# app.include_router(dashboard.router, prefix=settings.API_V1_PREFIX, tags=["Dashboard"])
