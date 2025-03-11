# Frontend API Reference

This documentation covers the DomainForge frontend TypeScript libraries and React components.

## Core Domain Types

```typescript
interface Entity {
    id: string;
    name: string;
    // ...other properties
}

type EntityId = string;
```

## Application Layer

```typescript
class EntityUseCase {
    async createEntity(entity: Entity): Promise<void>;
    async updateEntity(entity: Entity): Promise<void>;
    async deleteEntity(id: EntityId): Promise<void>;
}
```

## Services

```typescript
class HttpClient {
    async get<T>(url: string): Promise<T>;
    async post<T>(url: string, data: any): Promise<T>;
    async put<T>(url: string, data: any): Promise<T>;
    async delete(url: string): Promise<void>;
}

class EntityApiClient {
    async getEntity(id: EntityId): Promise<Entity>;
    async createEntity(entity: Entity): Promise<Entity>;
    async updateEntity(entity: Entity): Promise<Entity>;
    async deleteEntity(id: EntityId): Promise<void>;
}
```

## State Management

```typescript
class EntityStore {
    entities: Map<EntityId, Entity>;

    async load(id: EntityId): Promise<Entity>;
    async create(entity: Entity): Promise<void>;
    async update(entity: Entity): Promise<void>;
    async delete(id: EntityId): Promise<void>;
}
```

## React Hooks

### useStore

```typescript
function useStore(): RootStore;
```

Custom hook for accessing the application's state stores.

#### Example

```typescript
const MyComponent = observer(() => {
  const { entityStore } = useStore();
  // Use store...
});
```

### useEntity

```typescript
function useEntity(id: string): Entity | null;
```

Custom hook for fetching and managing entity data.

#### Example

```typescript
const MyComponent = observer(({ id }) => {
  const entity = useEntity(id);
  if (!entity) return null;
  // Render entity...
});
```
