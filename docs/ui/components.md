# UI Component Library

This documentation provides an overview of DomainForge's React component library.

## Core Components

### DomainModelVisualizer

The DomainModelVisualizer component provides an interactive visualization of your domain model, showing entities and their relationships.

```typescript
interface DomainModelVisualizerProps {
  model: DomainModel;
  onEntityClick?: (entityId: string) => void;
  onRelationshipClick?: (relationshipId: string) => void;
  layout?: "force" | "hierarchical" | "circular";
  theme?: VisualizerTheme;
}

const DomainModelVisualizer: React.FC<DomainModelVisualizerProps>;
```

For detailed examples and interactive documentation, visit our [Storybook Documentation](/storybook/index.html).

## Form Components

Our form components are built using Mantine and follow our design system guidelines.

### EntityForm

The EntityForm component provides a standardized way to create and edit entities.

```typescript
interface EntityFormProps {
  initialData?: Entity;
  onSubmit: (data: EntityFormData) => void | Promise<void>;
  onCancel?: () => void;
  isLoading?: boolean;
  error?: string;
}

const EntityForm: React.FC<EntityFormProps>;
```

### Example Usage

```tsx
import { EntityForm } from "@domainforge/ui";

const MyComponent = () => {
  const handleSubmit = data => {
    // Handle form submission
  };

  return <EntityForm onSubmit={handleSubmit} initialData={existingEntity} />;
};
```

## Data Display Components

### EntityList

A component for displaying lists of entities with filtering and sorting capabilities.

```typescript
interface EntityListProps {
  entities: Entity[];
  onEntityClick?: (entityId: string) => void;
  onDeleteClick?: (entityId: string) => void;
  isLoading?: boolean;
  error?: string;
}

const EntityList: React.FC<EntityListProps>;
```

### EntityDetail

A component for displaying detailed entity information.

```typescript
interface EntityDetailProps {
  entity: Entity;
  onEdit?: () => void;
  onDelete?: () => void;
  isLoading?: boolean;
  error?: string;
}

const EntityDetail: React.FC<EntityDetailProps>;
```

## Layout Components

### AppShell

The main layout component that provides navigation and consistent structure.

```typescript
interface AppShellProps {
  children: React.ReactNode;
  navigationItems?: NavigationItem[];
  headerContent?: React.ReactNode;
  theme?: AppTheme;
}

const AppShell: React.FC<AppShellProps>;
```

## Working with Components

### Best Practices

1. Use TypeScript for type safety
2. Follow our component composition patterns
3. Utilize hooks for state management
4. Keep components focused and single-responsibility
5. Write comprehensive tests using React Testing Library

### Theming

Components use our Mantine theme configuration. Customize the theme in your application:

```tsx
import { MantineProvider, createTheme } from '@mantine/core;

const theme = createTheme({
  primaryColor: 'blue',
  // Your customizations...
});

export const App = () => (
  <MantineProvider theme={theme}>
    <YourApp />
  </MantineProvider>
);
```
