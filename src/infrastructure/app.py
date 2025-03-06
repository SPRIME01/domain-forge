"""
FastAPI application configuration.

This module sets up the FastAPI application with all necessary middleware,
database connections, and route handlers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from contextlib import asynccontextmanager

from ..config.settings import get_settings
from .database import init_database
from ..api.controllers.entity_controller import router as entity_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    This context manager handles startup and shutdown events for the application.
    """
    # Get configuration
    settings = get_settings()

    # Create database engine
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
    )

    # Initialize database
    await init_database(engine)

    # Make engine available to the application
    app.state.engine = engine

    yield

    # Clean up
    await engine.dispose()


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        The configured FastAPI application
    """
    # Get configuration
    settings = get_settings()

    # Create FastAPI app
    app = FastAPI(
        title="API",
        description="API for bounded context",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    app.include_router(entity_router)

    return app


# Create the application instance
app = create_app()
