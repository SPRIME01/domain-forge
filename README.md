# 🏗️ DomainForge

[![CI Status](https://github.com/yourusername/domain-forge/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/domain-forge/actions/workflows/ci.yml)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPL--3.0-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

DomainForge is a powerful domain-driven code generation tool that transforms domain models into full-stack applications. It helps you build consistent, well-structured applications following clean architecture principles with minimal effort.

## ✨ Features

- **🔤 Domain-Specific Language (DSL)**: Define your domain model using a simple, intuitive language
- **🤖 AI-Guided Domain Modeling**: Conversational AI assistant helps you define your domain model
- **🏛️ Clean Architecture**: Generated code follows clean architecture principles and best practices
- **🚀 Full-Stack Generation**: Create both backend (Python FastAPI) and frontend (TypeScript React) applications
- **📝 Customizable Templates**: Modify templates to match your specific requirements
- **🧩 Domain-Driven Design**: Support for DDD concepts including bounded contexts, entities, value objects, and repositories
- **🔗 Entity Relationships**: Define relationships between entities with various cardinalities
- **🌐 API Generation**: Automatic REST API generation with OpenAPI documentation
- **💻 UI Generation**: Generate React components including forms, tables, and detail views
- **✅ Validation**: Built-in validation rules for entity properties
- **🧪 Testing**: Generated test suite with unit and integration tests
- **🗄️ Database Support**: SQL database support through SQLAlchemy
- **⚡ Async Support**: Fully async backend implementation for high performance

## 📦 Installation

```bash
# Install with pip
pip install domainforge

# Or install with uv (recommended)
uv pip install domainforge
```

## 🚀 Quick Start

### 🤖 Using the AI Assistant (New!)

1. Configure your OpenAI API key:

```bash
# Set your OpenAI API key in .env file
echo "OPENAI_API_KEY=your-api-key-here" > .env

# Or set as environment variable
export OPENAI_API_KEY=your-api-key-here  # Linux/Mac
set OPENAI_API_KEY=your-api-key-here     # Windows CMD
$env:OPENAI_API_KEY="your-api-key-here"  # Windows PowerShell
```

2. Start the AI assistant to help define your domain model:

```bash
domainforge assistant
```

3. Describe your application domain to the AI, which will guide you through defining:

   - 📦 Bounded contexts
   - 🏛️ Entities and their properties
   - 🔗 Relationships between entities
   - 📋 Business rules and constraints
   - 🌐 APIs and UI components

4. Once your domain model is complete, the assistant will generate the DSL code and create your application.

### 📝 Using DSL Directly

1. Create a `.domainforge` file that defines your domain model:

```
// Example domain model for a blog application
@Blog {
  #Post {
    id: UUID
    title: String [required, minLength:3, maxLength:100]
    content: Text [required]
    published: Boolean = false
    publishedAt: DateTime?

    publish() {
      // This will be implemented in the generated code
    }

    api: GET "/posts"
    api: GET "/posts/{id}"
    api: POST "/posts"
    api: PUT "/posts/{id}"
    api: DELETE "/posts/{id}"

    ui: Table
    ui: Form
  }

  #Comment {
    id: UUID
    postId: UUID [required]
    author: String [required]
    content: Text [required]
    createdAt: DateTime = "new Date()"

    api: GET "/posts/{id}/comments"
    api: POST "/posts/{id}/comments"
    api: DELETE "/comments/{id}"

    ui: Table
    ui: Form
  }

  Post => Comment
}
```

2. Generate your application:

```bash
domainforge generate blog.domainforge --output ./my-blog-app
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

## 🧰 Command-Line Options

```
domainforge [command] [options]

Commands:
  generate    Generate a full-stack application from DSL
  assistant   Start the AI assistant for guided domain modeling
  validate    Validate a DSL file without generating code
  visualize   Generate visual diagram of domain model

Options for 'generate':
  -i, --input <file>     Path to the .domainforge DSL file
  -o, --output <dir>     Output directory for generated code (default: ./output)
  --backend-only         Generate only the backend code
  --frontend-only        Generate only the frontend code
  --export-model         Export the domain model as JSON
  --model-path <path>    Path where the domain model should be exported
  -v, --verbose          Enable verbose output
  -h, --help             Show this help message and exit

Options for 'assistant':
  --api-key <key>        OpenAI API key (alternative to environment variable)
  --api-base <url>       Custom API base URL for alternative providers
  --model <model>        AI model to use (default: gpt-4)
```

## ⚙️ Configuration

### 🤖 OpenAI API Configuration

DomainForge's AI assistant uses the OpenAI API or any compatible API service. Configure it using:

1. Environment variables:

   - `OPENAI_API_KEY`: Your API key
   - `OPENAI_API_BASE`: Optional base URL for alternative providers
   - `OPENAI_MODEL`: Model to use (default: gpt-4)

2. `.env` file in project root:

   ```
   OPENAI_API_KEY=your-api-key-here
   OPENAI_API_BASE=https://your-api-provider.com/v1  # Optional
   OPENAI_MODEL=gpt-4  # Optional
   ```

3. Command line arguments (see options above)

### 🔄 Alternative AI Providers

DomainForge supports any OpenAI API-compatible service:

- Azure OpenAI Service
- Local LLM servers (e.g., LM Studio, llama.cpp, etc.)
- Other compatible API services

To use an alternative provider, specify the `OPENAI_API_BASE` URL.

## 📖 DSL Specification

The DomainForge DSL allows you to define your domain model in a clear, structured way. For full details, see the [DSL Specification](docs/dsl-specification.md).

### 🧱 Basic Components

- **📦 Bounded Contexts**: Represented with `@ContextName { ... }`
- **🏛️ Entities**: Represented with `#EntityName { ... }`
- **💎 Value Objects**: Represented with `%ValueObjectName { ... }`
- **🔗 Relationships**: Connected using various symbols like `=>`, `<->`, etc.
- **📊 Properties**: Defined as `name: Type [constraints]`
- **⚙️ Methods**: Defined as `methodName(parameters) { ... }`
- **🌐 API Endpoints**: Defined as `api: METHOD "/path"`
- **🖼️ UI Components**: Defined as `ui: ComponentType`

## 🖼️ UI Components

DomainForge supports the following UI components that can be defined within entities using the DSL:

1. **Form**: Typically used for data input/editing. Can have parameters defined through `ui_params` and can include a description in `ui_desc`.
2. **Table**: Used for displaying tabular data. Suitable for showing collections of entities.
3. **Card**: Represents entity data in a card format. Good for grid/dashboard layouts.
4. **Detail**: Shows detailed view of an entity. Useful for showing all properties of a single record.
5. **List**: Displays data in a list format. Suitable for simpler data presentations.

### Usage Example

Here's how you might define a UI component in the DSL:

```plaintext
#User {
    name: String
    email: String

    ui: Form (
        fields: List<String> = ["name", "email"]
    ) { "User registration form" }

    ui: Table (
        columns: List<String> = ["name", "email"]
    ) { "User management table" }
}
```

The grammar allows for:
- Optional parameters through `ui_params`
- Optional descriptions through `ui_desc`
- Multiple UI definitions per entity

## 🏛️ Architecture

DomainForge follows a clean architecture approach, generating code with the following layers:

### 🔙 Backend (Python FastAPI)

- **📦 Domain Layer**: Core entities, value objects, and repository interfaces
- **⚙️ Application Layer**: Use cases, DTOs, and application services
- **🛠️ Infrastructure Layer**: Database implementations, external services
- **🌐 API Layer**: Controllers, routes, and request/response models

### 🖥️ Frontend (TypeScript React)

- **📦 Domain Layer**: Core entities and value objects
- **⚙️ Application Layer**: Use cases and application services
- **🛠️ Infrastructure Layer**: API clients and state management
- **💻 UI Layer**: React components, pages, and hooks

For more details, see the [Architecture Specification](docs/architecture-specification.md).

## 👨‍💻 Development

### 📋 Prerequisites

- Python 3.8+
- Node.js 14+
- uv package manager (recommended) or pip

### 🛠️ Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/domain-forge.git
cd domain-forge

# Create and activate virtual environment
uv venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
uv pip install -e ".[dev]"
```

### 🧪 Running Tests

```bash
# Run all tests
uv run pytest tests/

# Run with coverage
uv run pytest --cov=domainforge tests/

# Run BDD tests
uv run pytest tests/bdd/
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -am 'Add new feature'`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Submit a pull request

## 📄 License

This project is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details.
