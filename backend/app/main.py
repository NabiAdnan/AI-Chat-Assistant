import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.database.mongodb import connect_to_mongo, close_mongo_connection, db_manager
from app.routes.chat import router as chat_router
from app.routes.conversations import router as conversations_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("nexus_ai")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Nexus AI backend...")
    try:
        await connect_to_mongo()
        logger.info("MongoDB initialized successfully.")
    except Exception as exc:
        logger.error("MongoDB failed to connect during startup: %s", exc)
    yield
    logger.info("Shutting down Nexus AI backend...")
    await close_mongo_connection()


app = FastAPI(
    title="Nexus AI Chat Assistant API",
    description=(
        "Production-grade backend for Nexus AI: supports Server-Sent Events (SSE) streaming, "
        "persona/tone adaptation (Professional, Casual, Concise), OpenAI GPT integration, "
        "and persistent conversation history in MongoDB."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:[0-9]+)?$",
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        settings.FRONTEND_URL.rstrip("/"),
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers with /api prefix
app.include_router(chat_router, prefix="/api")
app.include_router(conversations_router, prefix="/api")


@app.get("/api/health", tags=["Health"])
async def health_check():
    """Health status endpoint checking server and database state."""
    db_connected = False
    if db_manager.client is not None:
        try:
            await db_manager.client.admin.command("ping")
            db_connected = True
        except Exception:
            db_connected = False

    return {
        "status": "healthy" if db_connected else "degraded",
        "service": "Nexus AI Backend",
        "version": "1.0.0",
        "database": "connected" if db_connected else "disconnected",
    }


@app.get("/", include_in_schema=False)
async def root():
    return {
        "message": "Welcome to Nexus AI Backend API. Explore documentation at /docs",
        "documentation": "/docs",
        "health": "/api/health",
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception for %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Please try again later."},
    )
