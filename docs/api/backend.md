# Backend API Reference

This documentation covers the DomainForge backend REST API.

## Authentication

All API endpoints require authentication using a bearer token:

```http
Authorization: Bearer <your-token>
```

## Domain Model API

### Create Domain Model

`POST /api/models`

Creates a new domain model from DSL specification.

#### Request

```json
{
  "name": "blog",
  "dsl_content": "@Blog { ... }"
}
```

#### Response

```json
{
  "id": "uuid",
  "name": "blog",
  "status": "created"
}
```

### Generate Code

`POST /api/models/{id}/generate`

Generates code from a domain model.

#### Request

```json
{
  "output_path": "./my-app",
  "options": {
    "backend": true,
    "frontend": true
  }
}
```

#### Response

```json
{
  "status": "success",
  "output_path": "./my-app"
}
```

## REST API Endpoints

### Entity Management

::: domainforge.api.controllers.entity_controller
    options:
      show_root_heading: true
      heading_level: 3

## WebSocket API

For real-time features like code generation progress updates, we provide WebSocket endpoints:

- `/ws/generation/{model_id}` - Code generation progress updates
- `/ws/chat` - Interactive AI assistance
