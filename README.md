# DomainForge

DomainForge is a powerful domain-driven code generation tool that transforms domain models into full-stack applications. It helps you build consistent, well-structured applications following clean architecture principles with minimal effort.

## Features

- **Domain-Specific Language (DSL)**: Define your domain model using a simple, intuitive language
- **Clean Architecture**: Generated code follows clean architecture principles
- **Full-Stack Generation**: Create both backend (Python FastAPI) and frontend (TypeScript React) applications
- **Customizable Templates**: Modify templates to match your specific requirements
- **Bounded Contexts**: Support for DDD bounded contexts
- **Entity Relationships**: Define relationships between entities
- **API Generation**: Automatic REST API generation
- **UI Generation**: Generate React components and forms

## Installation

```bash
pip install domainforge
```

## Quick Start

1. Create a `.domainforge` file that defines your domain model:

```
// Example domain model for a blog application
BoundedContext Blog {
  Entity Post {
    id: UUID
    title: String [required, minLength:3, maxLength:100]
    content: Text [required]
    published: Boolean = false
    publishedAt: DateTime?

    method publish() {
      // This will be implemented in the generated code
    }

    Repository PostRepository

    API {
      GET /posts
      GET /posts/{id}
      POST /posts
      PUT /posts/{id}
      DELETE /posts/{id}
    }

    UI {
      Table
      Form
    }
  }

  Entity Comment {
    id: UUID
    postId: UUID [required]
    author: String [required]
    content: Text [required]
    createdAt: DateTime = "new Date()"

    Repository CommentRepository

    API {
      GET /posts/{id}/comments
      POST /posts/{id}/comments
      DELETE /comments/{id}
    }

    UI {
      Table
      Form
    }
  }
}
```

2. Generate your application:

```bash
domainforge blog.domainforge --output ./my-blog-app
```

3. Run the generated applications:

```bash
# Backend (FastAPI)
cd my-blog-app/backend
pip install -r requirements.txt
uvicorn src.main:app --reload

# Frontend (React)
cd my-blog-app/frontend
npm install
npm run dev
```

## Command-Line Options

```
domainforge [options] <input_file>

Arguments:
  input_file              Path to the .domainforge DSL file

Options:
  -o, --output <dir>      Output directory for generated code (default: ./output)
  --backend-only          Generate only the backend code
  --frontend-only         Generate only the frontend code
  --export-model          Export the domain model as JSON
  --model-path <path>     Path where the domain model should be exported
  -v, --verbose           Enable verbose output
  -h, --help              Show this help message and exit
```

## DSL Specification

The DomainForge DSL allows you to define your domain model in a clear, structured way. For full details, see the [DSL Specification](docs/dsl-specification.md).

## Architecture

DomainForge follows a clean architecture approach, generating code with the following layers:

### Backend (Python FastAPI)
- **Domain Layer**: Core entities, value objects, and repository interfaces
- **Application Layer**: Use cases, DTOs, and application services
- **Infrastructure Layer**: Database implementations, external services
- **API Layer**: Controllers, routes, and request/response models

### Frontend (TypeScript React)
- **Domain Layer**: Core entities and value objects
- **Application Layer**: Use cases and application services
- **Infrastructure Layer**: API clients and state management
- **UI Layer**: React components, pages, and hooks

For more details, see the [Architecture Specification](docs/architecture-specification.md).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the GPL-3.0 License - see the LICENSE file for details.
