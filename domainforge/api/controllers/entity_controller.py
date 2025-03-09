"""Entity API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from domainforge.api.models import Entity
from domainforge.infrastructure.database import get_session


class EntityModel(BaseModel):
    """Entity data model."""

    name: str = Field(..., min_length=1, max_length=100)


class EntityResponse(EntityModel):
    """Entity response model."""

    id: int
    model_config = ConfigDict(from_attributes=True)


router = APIRouter(prefix="/api/entities", tags=["entities"])


@router.post("/", response_model=EntityResponse, status_code=201)
async def create_entity(
    entity: Annotated[EntityModel, ...],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Entity:
    """Create a new entity."""
    try:
        result = await session.execute(
            insert(Entity).values(name=entity.name).returning(Entity)
        )
        created_entity = result.scalar_one()
        await session.commit()
        return created_entity
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{entity_id}", response_model=EntityResponse)
async def get_entity(
    entity_id: Annotated[int, ...],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Entity:
    """Get an entity by ID."""
    try:
        result = await session.execute(select(Entity).where(Entity.id == entity_id))
        entity = result.scalar_one_or_none()
        if not entity:
            raise HTTPException(status_code=404, detail="Entity not found")
        return entity
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{entity_id}", response_model=EntityResponse)
async def update_entity(
    entity_id: Annotated[int, ...],
    entity: Annotated[EntityModel, ...],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Entity:
    """Update an entity."""
    try:
        result = await session.execute(
            update(Entity)
            .where(Entity.id == entity_id)
            .values(name=entity.name)
            .returning(Entity)
        )
        updated_entity = result.scalar_one_or_none()
        if not updated_entity:
            raise HTTPException(status_code=404, detail="Entity not found")
        await session.commit()
        return updated_entity
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{entity_id}", status_code=204)
async def delete_entity(
    entity_id: Annotated[int, ...],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    """Delete an entity."""
    # BEGIN SECURITY CHECKS
    try:
        result = await session.execute(
            delete(Entity).where(Entity.id == entity_id).returning(Entity)
        )
        deleted_entity = result.scalar_one_or_none()
        if not deleted_entity:
            raise HTTPException(status_code=404, detail="Entity not found")
        await session.commit()
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    # END SECURITY CHECKS
