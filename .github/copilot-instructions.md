# GitHub Copilot Custom Instructions

## Code Generation Guidelines

### General Best Practices
- Generate code that strictly follows best practices
- Focus on readability, maintainability, and testability

### Python Standards
- Follow PEP8 standards with clear variable names
- Include mandatory docstrings
- Use strict typing (mypy compatible)
- Implement async methods for performance
- Prefer `typing.Protocol` over abstract base classes
- Follow Domain-Driven Design principles
- Use message bus and ports & adapters patterns
- Use `pyproject.toml` for project configuration
- Use virtual environment with `uv`:
    - Create venv: `uv venv .venv`
    - Activate venv (Windows): `.venv\Scripts\activate`
    - Activate venv (Unix): `source .venv/bin/activate`
    - Always check/create/activate venv before operations
- Use `uv` package manager for dependencies:
    - Install packages: `uv pip install <package>`
    - Add to pyproject.toml: `uv pip install --upgrade <package>`
    - Run tests: `uv run pytest tests/  -v`

### TypeScript Standards
- Follow ES6+ standards
- Use strict type annotations
- Implement modular design
- Apply proper interfaces and patterns

### Naming Conventions
- Classes/Objects: Singular nouns (e.g., `Customer`)
- Methods/Functions: Action verbs (e.g., `processPayment`)
- Boolean Variables: Use "is", "has", "must" prefix
- Other Variables: Clear, descriptive noun phrases

## Production Readiness

### Python Requirements
- Comprehensive exception handling
- Resource cleanup management
- Testing with pytest, pytest-BDD, coverage, and mocks (`uv pip run pytest`)
- Security checks and input validation
- Package management with `uv`
- Project configuration in `pyproject.toml`

### TypeScript Requirements
- Async error management
- Input validation
- CI/CD pipeline integration
- Testing with Jest

### Special Code Blocks

#### Performance Optimization
Python:
```python
# BEGIN PERFORMANCE OPTIMIZATION
# END PERFORMANCE OPTIMIZATION
```

TypeScript:
```typescript
// BEGIN PERFORMANCE OPTIMIZATION
// END PERFORMANCE OPTIMIZATION
```

#### Security Checks
Python:
```python
# BEGIN SECURITY CHECKS
# END SECURITY CHECKS
```

TypeScript:
```typescript
// BEGIN SECURITY CHECKS
// END SECURITY CHECKS
```

### Inline Commands
- Refactor: `# copilot: refactor` (Python) or `// copilot: refactor` (TypeScript)
- Optimize: `# copilot: optimize` (Python) or `// copilot: optimize` (TypeScript)

### Testing Approach
- Follow Test-Driven Development (TDD)
- Generate test stubs before implementation
- Use pytest/pytest-BDD for Python (run with `uv pip run pytest`)
- Use Jest for TypeScript

