# Documentation Standards

## General Guidelines
- All code must be documented with clear, concise comments
- Documentation should explain "why" rather than "what"
- Every module, class, and function must have a docstring
- Use type hints meaningfully but avoid redundancy
- Follow clean code principles:
    - Single Responsibility Principle
    - DRY (Don't Repeat Yourself)
    - KISS (Keep It Simple, Stupid)
    - YAGNI (You Aren't Gonna Need It)

## Python Docstring Format
# GitHub Copilot Custom Instructions

## Code Generation Guidelines

### General Best Practices
- Generate code that strictly follows best practices
- Focus on readability, maintainability, and testability
- Follow consistent naming conventions throughout codebase
- Create feature branches for each new feature using format: `feature/<feature-name>`

### Branch Management
- Never work directly on main/master branch
- Create new branch for each feature: `git checkout -b feature/<feature-name>`
- Use kebab-case for feature names: `feature/user-authentication`
- Keep features small and focused
- Delete branches after merging
- Use pull requests for code reviews and merging
- Ensure all tests pass before merging
- Use descriptive commit messages
- Commit often with small, logical changes

### Python Standards
- Follow PEP8 standards with clear variable names
- Use strict typing (mypy compatible)
- Avoid using `Any` type unless absolutely necessary
- Use `typing.Protocol` for interfaces by default
- Only use ABC when Protocol cannot fulfill requirements
- Use Pydantic for all data structures and validation
- Implement async methods for performance
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
- Constants: UPPERCASE with underscores
- Private members: Start with underscore
- Interfaces: Start with "I" (TypeScript)
- Types: PascalCase (TypeScript)

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
