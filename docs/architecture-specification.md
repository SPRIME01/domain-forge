# A General-Purpose Application Framework with Python Backend and TypeScript Frontend

## Architecture Overview

AutoApp is a general-purpose application framework using Domain-Driven Design (DDD) and clean architecture principles, with a Python backend and TypeScript frontend.

```
┌────────────────────────────────────────────────────────────────┐
│                      TypeScript Frontend                        │
│                                                                 │
│  ┌─────────────────┐     ┌────────────────┐    ┌────────────┐  │
│  │   Presentation  │     │   Application  │    │   Domain   │  │
│  │      Layer      │     │      Layer     │    │    Layer   │  │
│  │   (React/Vue)   │     │  (Use Cases)   │    │  (Models)  │  │
│  └────────┬────────┘     └────────┬───────┘    └─────┬──────┘  │
│           │                       │                   │         │
│           │                       │                   │         │
│           └───────────────────────┼───────────────────┘         │
│                                   │                             │
│                          ┌────────┴────────┐                    │
│                          │  Infrastructure │                    │
│                          │     Layer       │                    │
│                          └────────┬────────┘                    │
└──────────────────────────────────│──────────────────────────────┘
                                  API
                                   │
┌──────────────────────────────────│──────────────────────────────┐
│                                  │                              │
│                          ┌───────┴─────────┐                    │
│                          │  API Controllers │                   │
│                          │    (FastAPI)     │                   │
│                          └───────┬─────────┘                    │
│                                  │                              │
│ ┌─────────────────┐     ┌───────┴────────┐     ┌────────────┐  │
│ │   Application   │     │     Domain     │     │ Infrastructure│ │
│ │      Layer      │◄───►│      Layer     │◄───►│     Layer    │ │
│ │   (Use Cases)   │     │ (Entities/Logic)│    │ (Persistence) │ │
│ └─────────────────┘     └────────────────┘     └────────────┘  │
│                                                                 │
│                       Python Backend                            │
└─────────────────────────────────────────────────────────────────┘
```

## 1. Python Backend Implementation

### Project Structure

```
backend/
├── src/
│   ├── domain/                # Domain model - entities, value objects
│   │   ├── common/            # Shared domain concepts
│   │   └── [bounded-context]/ # Specific domain areas
│   ├── application/           # Use cases, commands, queries
│   ├── ports/                 # Interface adapters
│   │   ├── input/             # Primary ports (API interfaces)
│   │   └── output/            # Secondary ports (repository interfaces)
│   ├── adapters/              # Implementations of ports
│   │   ├── primary/           # API controllers
│   │   └── secondary/         # DB repositories, external services
│   ├── infrastructure/        # Technical concerns
│   │   ├── persistence/       # Database configuration
│   │   ├── messaging/         # Event bus implementation
│   │   └── config/            # Configuration settings
│   └── main.py                # Application bootstrap
├── tests/                     # Test suite
├── pyproject.toml             # Dependencies and project metadata
└── README.md                  # Documentation
```

### Core Domain Components (Python)

```python
# domainforge/domain/common/value_objects/entity_id.py
import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class EntityId:
    value: str

    @classmethod
    def generate(cls) -> 'EntityId':
        return cls(str(uuid.uuid4()))

    def __eq__(self, other):
        if not isinstance(other, EntityId):
            return False
        return self.value == other.value


# domainforge/domain/common/events/domain_event.py
from abc import ABC
from datetime import datetime
import uuid
from dataclasses import dataclass, field


@dataclass
class DomainEvent(ABC):
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_on: datetime = field(default_factory=datetime.now)


# domainforge/domain/common/events/event_bus.py
from abc import ABC, abstractmethod
from typing import Callable, Dict, List, Type
from .domain_event import DomainEvent


class EventHandler(ABC):
    @abstractmethod
    def handle(self, event: DomainEvent) -> None:
        pass


class EventBus(ABC):
    @abstractmethod
    def publish(self, event: DomainEvent) -> None:
        pass

    @abstractmethod
    def subscribe(self, event_type: Type[DomainEvent], handler: EventHandler) -> None:
        pass


# domainforge/domain/entity/entity.py
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional
from ..common.value_objects.entity_id import EntityId


class EntityType(Enum):
    DOCUMENT = "document"
    PRODUCT = "product"
    USER = "user"
    # Other entity types


@dataclass
class Value:
    type: str
    data: any


@dataclass
class Entity:
    id: EntityId
    type: EntityType
    attributes: Dict[str, Value] = field(default_factory=dict)

    def get_attribute(self, name: str) -> Optional[Value]:
        return self.attributes.get(name)

    def set_attribute(self, name: str, value: Value) -> None:
        self.attributes[name] = value

    def validate_state(self) -> bool:
        # Domain validation logic
        return True


# domainforge/domain/entity/events/entity_created_event.py
from ...common.events.domain_event import DomainEvent
from ...common.value_objects.entity_id import EntityId
from ..entity import EntityType


class EntityCreatedEvent(DomainEvent):
    def __init__(self, entity_id: EntityId, entity_type: EntityType):
        super().__init__()
        self.entity_id = entity_id
        self.entity_type = entity_type


# domainforge/domain/entity/repositories/entity_repository.py
from abc import ABC, abstractmethod
from typing import Optional
from ..entity import Entity
from ...common.value_objects.entity_id import EntityId


class EntityRepository(ABC):
    @abstractmethod
    async def find_by_id(self, id: EntityId) -> Optional[Entity]:
        pass

    @abstractmethod
    async def save(self, entity: Entity) -> None:
        pass

    @abstractmethod
    async def delete(self, id: EntityId) -> None:
        pass
```

### Application Layer (Python)

```python
# domainforge/application/dto/entity_dto.py
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class EntityDto:
    id: str
    type: str
    attributes: Dict[str, Any]


# domainforge/application/mappers/entity_mapper.py
from ...domain.entity.entity import Entity, EntityType, Value
from ...domain.common.value_objects.entity_id import EntityId
from ..dto.entity_dto import EntityDto


class EntityMapper:
    @staticmethod
    def to_domain(dto: EntityDto) -> Entity:
        entity_id = EntityId(dto.id)
        entity_type = EntityType(dto.type)

        attributes = {}
        for key, value in dto.attributes.items():
            attributes[key] = Value(
                type=type(value).__name__,
                data=value
            )

        return Entity(id=entity_id, type=entity_type, attributes=attributes)

    @staticmethod
    def to_dto(entity: Entity) -> EntityDto:
        attributes = {}
        for key, value in entity.attributes.items():
            attributes[key] = value.data

        return EntityDto(
            id=entity.id.value,
            type=entity.type.value,
            attributes=attributes
        )


# domainforge/application/use_cases/entity_use_case.py
from abc import ABC, abstractmethod
from ..dto.entity_dto import EntityDto
from ...domain.common.value_objects.entity_id import EntityId
from ...domain.entity.repositories.entity_repository import EntityRepository
from ...domain.common.events.event_bus import EventBus
from ...domain.entity.events.entity_created_event import EntityCreatedEvent
from ..mappers.entity_mapper import EntityMapper


class EntityUseCase(ABC):
    @abstractmethod
    async def get_entity(self, id: str) -> EntityDto:
        pass

    @abstractmethod
    async def create_entity(self, entity_dto: EntityDto) -> None:
        pass

    @abstractmethod
    async def update_entity(self, id: str, entity_dto: EntityDto) -> None:
        pass


class EntityUseCaseImpl(EntityUseCase):
    def __init__(
        self,
        entity_repository: EntityRepository,
        event_bus: EventBus
    ):
        self.entity_repository = entity_repository
        self.event_bus = event_bus

    async def get_entity(self, id: str) -> EntityDto:
        entity_id = EntityId(id)
        entity = await self.entity_repository.find_by_id(entity_id)

        if not entity:
            raise ValueError(f"Entity with id {id} not found")

        return EntityMapper.to_dto(entity)

    async def create_entity(self, entity_dto: EntityDto) -> None:
        entity = EntityMapper.to_domain(entity_dto)

        if not entity.validate_state():
            raise ValueError("Invalid entity state")

        await self.entity_repository.save(entity)

        # Publish domain event
        self.event_bus.publish(
            EntityCreatedEvent(entity.id, entity.type)
        )

    async def update_entity(self, id: str, entity_dto: EntityDto) -> None:
        # Implementation
        pass
```

### Infrastructure Layer (Python)

```python
# domainforge/infrastructure/messaging/in_memory_event_bus.py
from typing import Dict, List, Type
from ...domain.common.events.domain_event import DomainEvent
from ...domain.common.events.event_bus import EventBus, EventHandler


class InMemoryEventBus(EventBus):
    def __init__(self):
        self.handlers: Dict[Type[DomainEvent], List[EventHandler]] = {}

    def publish(self, event: DomainEvent) -> None:
        event_type = type(event)

        if event_type in self.handlers:
            for handler in self.handlers[event_type]:
                handler.handle(event)

    def subscribe(self, event_type: Type[DomainEvent], handler: EventHandler) -> None:
        if event_type not in self.handlers:
            self.handlers[event_type] = []

        self.handlers[event_type].append(handler)


# domainforge/infrastructure/persistence/sqlalchemy/models.py
from sqlalchemy import Column, String, JSON, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class EntityModel(Base):
    __tablename__ = "entities"

    id = Column(String, primary_key=True)
    type = Column(String, nullable=False)
    attributes = Column(JSON, nullable=False)


# domainforge/infrastructure/persistence/sqlalchemy/repositories/entity_repository.py
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .....domain.common.value_objects.entity_id import EntityId
from .....domain.entity.entity import Entity, EntityType, Value
from .....domain.entity.repositories.entity_repository import EntityRepository
from ..models import EntityModel


class SqlAlchemyEntityRepository(EntityRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_id(self, id: EntityId) -> Optional[Entity]:
        query = select(EntityModel).where(EntityModel.id == id.value)
        result = await self.session.execute(query)
        entity_model = result.scalars().first()

        if not entity_model:
            return None

        attributes = {}
        for key, value in entity_model.attributes.items():
            attributes[key] = Value(
                type=type(value).__name__,
                data=value
            )

        return Entity(
            id=EntityId(entity_model.id),
            type=EntityType(entity_model.type),
            attributes=attributes
        )

    async def save(self, entity: Entity) -> None:
        attributes_dict = {}
        for key, value in entity.attributes.items():
            attributes_dict[key] = value.data

        entity_model = EntityModel(
            id=entity.id.value,
            type=entity.type.value,
            attributes=attributes_dict
        )

        self.session.add(entity_model)
        await self.session.commit()

    async def delete(self, id: EntityId) -> None:
        query = select(EntityModel).where(EntityModel.id == id.value)
        result = await self.session.execute(query)
        entity_model = result.scalars().first()

        if entity_model:
            await self.session.delete(entity_model)
            await self.session.commit()
```

### API Controllers (Python with FastAPI)

```python
# domainforge/adapters/primary/api/entity_controller.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ....application.dto.entity_dto import EntityDto
from ....application.use_cases.entity_use_case import EntityUseCase
from ....infrastructure.dependency_injection import get_entity_use_case

router = APIRouter(prefix="/api/entities", tags=["entities"])

@router.get("/{id}", response_model=EntityDto)
async def get_entity(id: str, use_case: EntityUseCase = Depends(get_entity_use_case)):
    try:
        return await use_case.get_entity(id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_entity(entity_dto: EntityDto, use_case: EntityUseCase = Depends(get_entity_use_case)):
    try:
        await use_case.create_entity(entity_dto)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{id}")
async def update_entity(id: str, entity_dto: EntityDto, use_case: EntityUseCase = Depends(get_entity_use_case)):
    try:
        await use_case.update_entity(id, entity_dto)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# domainforge/main.py
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .adapters.primary.api.entity_controller import router as entity_router
from .infrastructure.config.settings import get_settings

app = FastAPI(title="AutoAPP API")

# Configure CORS
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(entity_router)

if __name__ == "__main__":
    uvicorn.run("domainforge.main:app", host="0.0.0.0", port=8000, reload=True)
```

### Dependency Injection (Python)

```python
# domainforge/infrastructure/dependency_injection.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from .persistence.sqlalchemy.database import get_session
from .messaging.in_memory_event_bus import InMemoryEventBus
from .persistence.sqlalchemy.repositories.entity_repository import SqlAlchemyEntityRepository
from ..domain.common.events.event_bus import EventBus
from ..domain.entity.repositories.entity_repository import EntityRepository
from ..application.use_cases.entity_use_case import EntityUseCase, EntityUseCaseImpl

# Singleton instances
_event_bus = InMemoryEventBus()

def get_event_bus() -> EventBus:
    return _event_bus

def get_entity_repository(session: AsyncSession = Depends(get_session)) -> EntityRepository:
    return SqlAlchemyEntityRepository(session)

def get_entity_use_case(
    repository: EntityRepository = Depends(get_entity_repository),
    event_bus: EventBus = Depends(get_event_bus)
) -> EntityUseCase:
    return EntityUseCaseImpl(repository, event_bus)
```

## 2. TypeScript Frontend Implementation

### Project Structure

```
frontend/
├── src/
│   ├── domain/                # Domain models
│   │   ├── entity/            # Entity models
│   │   └── events/            # Domain events
│   ├── application/           # Application logic
│   │   ├── dto/               # Data transfer objects
│   │   ├── ports/             # Interface for infrastructure
│   │   └── useCases/          # Use cases implementing business logic
│   ├── infrastructure/        # External dependencies
│   │   ├── api/               # API clients
│   │   ├── http/              # HTTP utilities
│   │   └── store/             # State management
│   ├── ui/                    # UI components
│   │   ├── components/        # Reusable components
│   │   ├── pages/             # Page components
│   │   └── layouts/           # Layout components
│   ├── App.tsx                # Main application component
│   └── main.tsx               # Application entry point
├── index.html                 # HTML entry point
├── tsconfig.json              # TypeScript configuration
├── vite.config.ts             # Build configuration
└── package.json               # Dependencies and scripts
```

### Core Domain Models (TypeScript)

```typescript
// src/domain/entity/EntityId.ts
export class EntityId {
  constructor(public readonly value: string) {
    if (!value) throw new Error("EntityId cannot be empty");
  }

  equals(other: EntityId): boolean {
    return this.value === other.value;
  }

  static generate(): EntityId {
    return new EntityId(crypto.randomUUID());
  }
}

// src/domain/entity/EntityTypes.ts
export enum EntityType {
  DOCUMENT = "document",
  PRODUCT = "product",
  USER = "user",
}

export interface Value {
  readonly type: string;
  readonly data: any;
}

// src/domain/entity/Entity.ts
import { EntityId } from "./EntityId";
import { EntityType, Value } from "./EntityTypes";

export class Entity {
  constructor(
    private readonly id: EntityId,
    private readonly type: EntityType,
    private attributes: Map<string, Value> = new Map()
  ) {}

  getId(): EntityId {
    return this.id;
  }

  getType(): EntityType {
    return this.type;
  }

  getAttribute(name: string): Value | undefined {
    return this.attributes.get(name);
  }

  setAttribute(name: string, value: Value): void {
    this.attributes.set(name, value);
  }

  getAllAttributes(): Map<string, Value> {
    return new Map(this.attributes);
  }

  validateState(): boolean {
    // Domain validation logic
    return true;
  }
}

// src/domain/events/DomainEvent.ts
export abstract class DomainEvent {
  public readonly eventId: string;
  public readonly occurredOn: Date;

  protected constructor() {
    this.eventId = crypto.randomUUID();
    this.occurredOn = new Date();
  }
}

// src/domain/events/EntityCreatedEvent.ts
import { DomainEvent } from "./DomainEvent";
import { EntityId } from "../entity/EntityId";
import { EntityType } from "../entity/EntityTypes";

export class EntityCreatedEvent extends DomainEvent {
  constructor(
    public readonly entityId: EntityId,
    public readonly type: EntityType
  ) {
    super();
  }
}
```

### Application Layer (TypeScript)

```typescript
// src/application/dto/EntityDto.ts
export interface EntityDto {
  id: string;
  type: string;
  attributes: Record<string, any>;
}

// src/application/ports/EntityRepository.ts
import { Entity } from "../../domain/entity/Entity";
import { EntityId } from "../../domain/entity/EntityId";

export interface EntityRepository {
  findById(id: EntityId): Promise<Entity | null>;
  save(entity: Entity): Promise<void>;
  delete(id: EntityId): Promise<void>;
}

// src/application/ports/ApiClient.ts
import { EntityDto } from "../dto/EntityDto";

export interface ApiClient {
  getEntity(id: string): Promise<EntityDto>;
  createEntity(entity: EntityDto): Promise<void>;
  updateEntity(id: string, entity: EntityDto): Promise<void>;
  deleteEntity(id: string): Promise<void>;
}

// src/application/useCases/EntityUseCase.ts
import { EntityDto } from "../dto/EntityDto";
import { ApiClient } from "../ports/ApiClient";
import { EntityId } from "../../domain/entity/EntityId";
import { Entity } from "../../domain/entity/Entity";
import { EntityType, Value } from "../../domain/entity/EntityTypes";

export class EntityUseCase {
  constructor(private apiClient: ApiClient) {}

  async getEntity(id: string): Promise<Entity> {
    const dto = await this.apiClient.getEntity(id);
    return this.mapDtoToDomain(dto);
  }

  async createEntity(entity: Entity): Promise<void> {
    if (!entity.validateState()) {
      throw new Error("Invalid entity state");
    }

    const dto = this.mapDomainToDto(entity);
    await this.apiClient.createEntity(dto);
  }

  async updateEntity(id: string, entity: Entity): Promise<void> {
    if (!entity.validateState()) {
      throw new Error("Invalid entity state");
    }

    const dto = this.mapDomainToDto(entity);
    await this.apiClient.updateEntity(id, dto);
  }

  async deleteEntity(id: string): Promise<void> {
    await this.apiClient.deleteEntity(id);
  }

  private mapDtoToDomain(dto: EntityDto): Entity {
    const id = new EntityId(dto.id);
    const type = dto.type as EntityType;
    const attributes = new Map<string, Value>();

    Object.entries(dto.attributes).forEach(([key, value]) => {
      attributes.set(key, {
        type: typeof value,
        data: value,
      });
    });

    return new Entity(id, type, attributes);
  }

  private mapDomainToDto(entity: Entity): EntityDto {
    const attributes: Record<string, any> = {};

    entity.getAllAttributes().forEach((value, key) => {
      attributes[key] = value.data;
    });

    return {
      id: entity.getId().value,
      type: entity.getType(),
      attributes,
    };
  }
}
```

### Infrastructure Layer (TypeScript)

```typescript
// src/infrastructure/http/HttpClient.ts
export class HttpClient {
  constructor(private baseUrl: string) {}

  async get<T>(url: string): Promise<T> {
    const response = await fetch(`${this.baseUrl}${url}`);

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    return response.json();
  }

  async post<T>(url: string, data: any): Promise<T> {
    const response = await fetch(`${this.baseUrl}${url}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    return response.json();
  }

  async put<T>(url: string, data: any): Promise<T> {
    const response = await fetch(`${this.baseUrl}${url}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    return response.json();
  }

  async delete<T>(url: string): Promise<T> {
    const response = await fetch(`${this.baseUrl}${url}`, {
      method: "DELETE",
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    return response.json();
  }
}

// src/infrastructure/api/EntityApiClient.ts
import { ApiClient } from "../../application/ports/ApiClient";
import { EntityDto } from "../../application/dto/EntityDto";
import { HttpClient } from "../http/HttpClient";

export class EntityApiClient implements ApiClient {
  constructor(private httpClient: HttpClient) {}

  async getEntity(id: string): Promise<EntityDto> {
    return this.httpClient.get<EntityDto>(`/api/entities/${id}`);
  }

  async createEntity(entity: EntityDto): Promise<void> {
    await this.httpClient.post<{ status: string }>("/api/entities/", entity);
  }

  async updateEntity(id: string, entity: EntityDto): Promise<void> {
    await this.httpClient.put<{ status: string }>(`/api/entities/${id}`, entity);
  }

  async deleteEntity(id: string): Promise<void> {
    await this.httpClient.delete<{ status: string }>(`/api/entities/${id}`);
  }
}

// src/infrastructure/store/EntityStore.ts
import { makeAutoObservable, runInAction } from "mobx";
import { Entity } from "../../domain/entity/Entity";
import { EntityUseCase } from "../../application/useCases/EntityUseCase";
import { EntityId } from "../../domain/entity/EntityId";
import { EntityType } from "../../domain/entity/EntityTypes";

export class EntityStore {
  entities: Map<string, Entity> = new Map();
  loading: boolean = false;
  error: string | null = null;

  constructor(private entityUseCase: EntityUseCase) {
    makeAutoObservable(this);
  }

  async fetchEntity(id: string) {
    this.loading = true;
    this.error = null;

    try {
      const entity = await this.entityUseCase.getEntity(id);

      runInAction(() => {
        this.entities.set(id, entity);
        this.loading = false;
      });
    } catch (error) {
      runInAction(() => {
        this.error = error instanceof Error ? error.message : "Unknown error";
        this.loading = false;
      });
    }
  }

  async createEntity(type: EntityType, attributes: Record<string, any>) {
    const id = EntityId.generate();
    const attributeMap = new Map();

    Object.entries(attributes).forEach(([key, value]) => {
      attributeMap.set(key, {
        type: typeof value,
        data: value,
      });
    });

    const entity = new Entity(id, type, attributeMap);

    this.loading = true;
    this.error = null;

    try {
      await this.entityUseCase.createEntity(entity);

      runInAction(() => {
        this.entities.set(id.value, entity);
        this.loading = false;
      });
    } catch (error) {
      runInAction(() => {
        this.error = error instanceof Error ? error.message : "Unknown error";
        this.loading = false;
      });
    }
  }
}
```

### UI Layer (TypeScript/React)

```typescript
// src/ui/components/EntityForm.tsx
import React, { useState } from 'react';
import { EntityType } from '../../domain/entity/EntityTypes';
import { observer } from 'mobx-react-lite';
import { useStore } from '../hooks/useStore';

interface EntityFormProps {
  onSubmit?: () => void;
}

const EntityForm: React.FC<EntityFormProps> = observer(({ onSubmit }) => {
  const { entityStore } = useStore();
  const [type, setType] = useState<EntityType>(EntityType.DOCUMENT);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    await entityStore.createEntity(type, {
      name,
      description,
      createdAt: new Date().toISOString()
    });

    setName('');
    setDescription('');

    if (onSubmit) {
      onSubmit();
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700">Type</label>
        <select
          value={type}
          onChange={(e) => setType(e.target.value as EntityType)}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
        >
          {Object.values(EntityType).map((value) => (
            <option key={value} value={value}>
              {value.charAt(0).toUpperCase() + value.slice(1)}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Name</label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Description</label>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={3}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
        />
      </div>

      <div>
        <button
          type="submit"
          disabled={entityStore.loading}
          className="inline-flex justify-center rounded-md border border-transparent bg-indigo-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
        >
          {entityStore.loading ? 'Saving...' : 'Create Entity'}
        </button>
      </div>

      {entityStore.error && (
        <div className="text-red-500 text-sm">{entityStore.error}</div>
      )}
    </form>
  );
});

export default EntityForm;

// src/ui/components/EntityList.tsx
import React, { useEffect } from 'react';
import { observer } from 'mobx-react-lite';
import { useStore } from '../hooks/useStore';
import { EntityId } from '../../domain/entity/EntityId';

const EntityList: React.FC = observer(() => {
  const { entityStore } = useStore();

  const entities = Array.from(entityStore.entities.values());

  return (
    <div className="mt-8">
      <h2 className="text-lg font-medium text-gray-900">Entities</h2>

      {entities.length === 0 ? (
        <p className="text-gray-500 mt-2">No entities created yet.</p>
      ) : (
        <ul className="mt-3 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {entities.map((entity) => (
            <li key={entity.getId().value} className="col-span-1 bg-white rounded-lg shadow divide-y divide-gray-200">
              <div className="w-full flex items-center justify-between p-6 space-x-6">
                <div className="flex-1 truncate">
                  <div className="flex items-center space-x-3">
                    <h3 className="text-gray-900 text-sm font-medium truncate">
                      {entity.getAttribute('name')?.data || 'Unnamed Entity'}
                    </h3>
                    <span className="flex-shrink-0 inline-block px-2 py-0.5 text-green-800 text-xs font-medium bg-green-100 rounded-full">
                      {entity.getType()}
                    </span>
                  </div>
                  <p className="mt-1 text-gray-500 text-sm truncate">
                    {entity.getAttribute('description')?.data || 'No description'}
                  </p>
                </div>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
});

export default EntityList;

// src/ui/pages/EntityPage.tsx
import React from 'react';
import EntityForm from '../components/EntityForm';
import EntityList from '../components/EntityList';

const EntityPage: React.FC = () => {
  return (
    <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div className="px-4 py-6 sm:px-0">
        <h1 className="text-2xl font-semibold text-gray-900">Entity Management</h1>

        <div className="mt-6 bg-white shadow px-4 py-5 sm:rounded-lg sm:p-6">
          <div className="md:grid md:grid-cols-3 md:gap-6">
            <div className="md:col-span-1">
              <h2 className="text-lg font-medium leading-6 text-gray-900">Create New Entity</h2>
              <p className="mt-1 text-sm text-gray-500">
                Create a new entity with a type and required attributes.
              </p>
            </div>
            <div className="mt-5 md:mt-0 md:col-span-2">
              <EntityForm />
            </div>
          </div>
        </div>

        <EntityList />
      </div>
    </div>
  );
};

export default EntityPage;
```

### Application Setup (TypeScript)

```typescript
// src/di/container.ts
import { HttpClient } from '../infrastructure/http/HttpClient';
import { EntityApiClient } from '../infrastructure/api/EntityApiClient';
import { EntityUseCase } from '../application/useCases/EntityUseCase';
import { EntityStore } from '../infrastructure/store/EntityStore';

// Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Create instances
const httpClient = new HttpClient(API_BASE_URL);
const entityApiClient = new EntityApiClient(httpClient);
const entityUseCase = new EntityUseCase(entityApiClient);
const entityStore = new EntityStore(entityUseCase);

// Root store
export const rootStore = {
  entityStore
};

export type RootStore = typeof rootStore;

// src/ui/hooks/useStore.ts
import { useContext } from 'react';
import { StoreContext } from '../providers/StoreProvider';
import type { RootStore } from '../../di/container';

export function useStore(): RootStore {
  const store = useContext(StoreContext);

  if (!store) {
    throw new Error('useStore must be used within a StoreProvider');
  }

  return store;
}

// src/ui/providers/StoreProvider.tsx
import React, { createContext, ReactNode } from 'react';
import { rootStore, RootStore } from '../../di/container';

export const StoreContext = createContext<RootStore | null>(null);

interface StoreProviderProps {
  children: ReactNode;
}

export const StoreProvider: React.FC<StoreProviderProps> = ({ children }) => {
  return (
    <StoreContext.Provider value={rootStore}>
      {children}
    </StoreContext.Provider>
  );
};

// src/App.tsx
import React from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { StoreProvider } from './ui/providers/StoreProvider';
import EntityPage from './ui/pages/EntityPage';

const App: React.FC = () => {
  return (
    <StoreProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<EntityPage />} />
        </Routes>
      </BrowserRouter>
    </StoreProvider>
  );
};

export default App;

// src/main.tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

## 3. Integration and Best Practices

### Communication Between Frontend and Backend

The frontend and backend communicate through a REST API. The backend exposes endpoints that the frontend consumes through the `EntityApiClient` class. This separation allows both parts to evolve independently while maintaining a clear contract.

### Dependency Injection

Both the frontend and backend use dependency injection to manage dependencies:

- Python backend uses FastAPI's dependency injection system
- TypeScript frontend uses a simple DI container for creating and providing service instances

### Event-Driven Architecture

The event-driven architecture is implemented through:

- Backend: An in-memory event bus that allows loose coupling between components
- Frontend: MobX stores that react to state changes and propagate updates to UI components

### Shared Models

While the frontend and backend have separate implementations of domain models, they share the same conceptual structure. The DTOs define the contract between the two layers, ensuring consistency.

## 4. Example Case Study: Document Management Feature

Let's examine how a document management feature would be implemented using this architecture:

1. **Domain Model**:

   - Define document-specific entities and value objects in both Python and TypeScript
   - Implement document-related domain events

2. **Application Layer**:

   - Create document use cases with specific business rules
   - Implement document DTOs and mappers

3. **Infrastructure**:

   - Implement document repositories in both languages
   - Create document-specific API endpoints

4. **UI Layer**:
   - Develop document management UI components
   - Implement document-specific views and forms

This approach allows for a clean separation of concerns while maintaining consistency across the stack.

## Conclusion

This is a general-purpose application framework with a Python backend and TypeScript frontend, providing a flexible, maintainable system that follows DDD and clean architecture principles. The ports and adapters pattern ensures loose coupling between components, while the event-driven architecture facilitates communication between bounded contexts.

This architecture provides several key benefits:

1. **Technology Flexibility**: The frontend and backend can evolve independently
2. **Maintainability**: Clean separation of concerns makes the codebase easier to maintain
3. **Testability**: Each layer can be tested in isolation
4. **Scalability**: The system can grow to accommodate new features and requirements
5. **Domain Focus**: Business logic remains at the core, independent of technical details

### Future Considerations
