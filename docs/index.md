# DomainForge Documentation

Welcome to the DomainForge documentation. This guide will help you understand and use DomainForge to generate full-stack applications from domain models.

## Overview

DomainForge is a powerful domain-driven code generation tool that transforms domain models into full-stack applications. It helps you build consistent, well-structured applications following clean architecture principles with minimal effort.

## Quick Start

### Installation

```bash
pip install domainforge
```

### Basic Usage

1. Create a domain model file:

```domainforge
@Blog {
  #Post {
    id: UUID
    title: String [required]
    content: Text [required]
    published: Boolean = false

    api: GET "/posts"
    ui: Form
  }
}
```

2. Generate your application:

```bash
domainforge generate blog.domainforge --output ./my-blog-app
```

## Documentation Structure

- **Architecture**: Detailed system architecture and design patterns
- **DSL Reference**: Complete specification of the DomainForge DSL
- **API Documentation**: Backend and frontend API references
- **UI Components**: Component library documentation

## Key Features

- Domain-Specific Language (DSL) for model definition
- Clean architecture code generation
- Full-stack application support (Python/TypeScript)
- Automated documentation
- API-first design
- Customizable templates

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](https://github.com/yourusername/domain-forge/blob/main/CONTRIBUTING.md) for more information.
