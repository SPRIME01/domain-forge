"""Entity API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.database import get_session
from pydantic import BaseModel, ConfigDict
from sqlalchemy import insert, select, update, delete
from src.api.models import Entity

class EntityModel(BaseModel):
    """Entity data model."""
    name: str

class EntityResponse(EntityModel):
    """Entity response model."""
    id: int
    model_config = ConfigDict(from_attributes=True)

router = APIRouter(prefix="/api/entities", tags=["entities"])

@router.post("", status_code=201, response_model=EntityResponse)
async def create_entity(entity: EntityModel, session: AsyncSession = Depends(get_session)) -> Entity:
    """Create a new entity."""
    result = await session.execute(
        insert(Entity).values(name=entity.name).returning(Entity)
    )
    created_entity = result.scalar_one()
    await session.commit()
    return created_entity

@router.get("/{entity_id}", response_model=EntityResponse)
async def get_entity(entity_id: int, session: AsyncSession = Depends(get_session)) -> Entity:
    """Get an entity by ID."""
    result = await session.execute(
        select(Entity).where(Entity.id == entity_id)
    )
    entity = result.scalar_one_or_none()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity

@router.put("/{entity_id}", response_model=EntityResponse)
async def update_entity(
    entity_id: int,
    entity: EntityModel,
    session: AsyncSession = Depends(get_session)
) -> Entity:
    """Update an entity."""
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

@router.delete("/{entity_id}", status_code=204)
async def delete_entity(entity_id: int, session: AsyncSession = Depends(get_session)) -> None:
    """Delete an entity."""
    result = await session.execute(
        delete(Entity).where(Entity.id == entity_id).returning(Entity)
    )
    deleted_entity = result.scalar_one_or_none()
    if not deleted_entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    await session.commit()
    return None
