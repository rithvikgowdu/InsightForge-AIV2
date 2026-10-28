from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.errors import (
    InsightForgeException,
    generic_exception_handler,
    insightforge_exception_handler,
)
from app.core.logging import logger
from app.models.base import Base
from app.core.database import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION} [{settings.ENVIRONMENT}]")
    # In development or test, verify database tables exist
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database schema validated.")
    except Exception as e:
        logger.warning(f"Database schema auto-creation notice: {str(e)}")
    yield
    logger.info("Shutting down InsightForge AI.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Discover real user pain points from public discussions and turn them into structured product opportunities.",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Exception Handlers
app.add_exception_handler(InsightForgeException, insightforge_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include API v1 Router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["Root"])
def root_status():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_PREFIX}/docs",
        "health": f"{settings.API_V1_PREFIX}/health",
    }

