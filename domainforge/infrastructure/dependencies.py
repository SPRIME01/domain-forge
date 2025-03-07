"""
Dependency injection configuration.

This module provides dependencies for FastAPI dependency injection system.
"""

from typing import Generator, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from ...application.use_cases.entity_use_case import EntityUseCase
from ...domain.context.repositories.entity_repository import EntityRepository
from ...application.services.entity_service import EntityService
from .database import get_session
from .repositories.entity_repository import SqlAlchemyEntityRepository


def get_db() -> Generator[Session, None, None]:
    """
    Get a database session.

    Returns:
        A database session generator
    """
    # ...existing code...
    yield  # Replace with actual session yielding


def get_entity_service(db: Session = Depends(get_db)) -> EntityService:
    """
    Get an Entity service instance.

    Args:
        db: The database session

    Returns:
        An instance of EntityService
    """
    # ...existing code...
    return EntityService()  # Replace with actual service instantiation


def get_entity_repository(db: Session = Depends(get_db)) -> EntityRepository:
    """
    Get an Entity repository instance.

    Args:
        db: The database session

    Returns:
        An instance of EntityRepository
    """
    # ...existing code...
    return SqlAlchemyEntityRepository(db)  # Replace with actual repository instantiation


async def get_entity_use_case(
    repository: EntityRepository = Depends(get_entity_repository),
) -> EntityUseCase:
    """
    Get a Entity use case instance.

    Args:
        repository: The repository to use

    Returns:
        An instance of EntityUseCase
    """
    return EntityUseCase(repository)
