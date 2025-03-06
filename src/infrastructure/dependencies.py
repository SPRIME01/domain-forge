"""
Dependency injection configuration.

This module provides dependencies for FastAPI dependency injection system.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_session
from ...domain.context.repositories.entity_repository import EntityRepository
from ...application.use_cases.entity_use_case import EntityUseCase
from .repositories.entity_repository import SqlAlchemyEntityRepository


async def get_entity_repository(
    session: AsyncSession = Depends(get_session)
) -> EntityRepository:
    """
    Get a Entity repository instance.

    Args:
        session: The database session

    Returns:
        An instance of EntityRepository
    """
    return SqlAlchemyEntityRepository(session)


async def get_entity_use_case(
    repository: EntityRepository = Depends(get_entity_repository)
) -> EntityUseCase:
    """
    Get a Entity use case instance.

    Args:
        repository: The repository to use

    Returns:
        An instance of EntityUseCase
    """
    return EntityUseCase(repository)
