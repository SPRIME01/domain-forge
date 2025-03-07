"""
Database configuration and session management.

This module provides the database configuration and session management utilities.
"""

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

# Create the declarative base class
Base = declarative_base()


async def init_database(engine: AsyncEngine) -> None:
    """
    Initialize the database.

    Args:
        engine: The SQLAlchemy engine to use
    """
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)


async def get_session(request: Request) -> AsyncSession:
    """
    Get a database session.

    Args:
        request: The FastAPI request object

    Returns:
        An async database session
    """
    engine = request.app.state.engine
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
