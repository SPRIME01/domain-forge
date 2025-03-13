# Plugin System

DomainForge features a flexible plugin system that allows you to extend its functionality in various ways. This guide explains how to use and create plugins.

## Plugin Types

DomainForge supports several types of plugins:

- **Validators**: Custom validation rules for domain models
- **Templates**: Custom code generation templates
- **Transformers**: Custom DSL transformation rules
- **Generators**: Custom code generators

## Using Plugins

### Installing Plugins

Use the CLI to manage plugins:

```bash
# List installed plugins
domainforge plugins list

# Install a plugin
domainforge plugins install my-plugin

# Install specific version
domainforge plugins install my-plugin --version 1.0.0

# Uninstall a plugin
domainforge plugins uninstall my-plugin

# Update all plugins
domainforge plugins update
```

### Using Custom Validators

```bash
# Use a custom validator
domainforge validate domain.df --validator custom-validator

# Use strict mode
domainforge validate domain.df --validator custom-validator --strict

# Get JSON output
domainforge validate domain.df --validator custom-validator --format json
```

### Using Custom Templates

```bash
# Generate with custom template
domainforge generate domain.df --template custom-template

# Specify frameworks
domainforge generate domain.df --template custom-template --backend fastapi --frontend react
```

## Creating Plugins

### Plugin Structure

A DomainForge plugin requires:

1. A `plugin.yaml` metadata file
2. A Python module implementing the plugin interface
3. Any additional resources (templates, schemas, etc.)

### Example: Validator Plugin

```python
from domainforge.plugins import Plugin, PluginMetadata, PluginType
from domainforge.plugins.validator import ValidatorPlugin, ValidationResult

class MyValidator(ValidatorPlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="my-validator",
            version="1.0.0",
            description="My custom validator",
            author="Your Name",
            plugin_type=PluginType.VALIDATOR,
        )

    def validate_model(self, model: str, strict: bool = False) -> ValidationResult:
        errors = []
        warnings = []
        # Add validation logic here
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )
```

### Example: Template Plugin

```python
from pathlib import Path
from domainforge.plugins import Plugin, PluginMetadata, PluginType

class MyTemplate(Plugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="my-template",
            version="1.0.0",
            description="My custom templates",
            author="Your Name",
            plugin_type=PluginType.TEMPLATE,
        )

    def get_template_paths(self) -> dict[str, Path]:
        template_dir = Path(__file__).parent / "templates"
        return {
            "backend": template_dir / "backend",
            "frontend": template_dir / "frontend",
        }
```

### Plugin Metadata

The `plugin.yaml` file defines your plugin's metadata:

```yaml
name: my-plugin
version: 1.0.0
description: My awesome plugin
author: Your Name
type: validator  # or template, transformer, generator
license: MIT
dependencies:
  - base-template >= 0.1.0
homepage: https://your-plugin-docs.com
documentation: https://your-plugin-docs.com/usage
```

### Template Files

For template plugins, organize your templates by framework:

```
my-template/
├── plugin.yaml
├── __init__.py
└── templates/
    ├── backend/
    │   ├── fastapi/
    │   │   └── entity.py.j2
    │   └── django/
    │       └── models.py.j2
    └── frontend/
        ├── react/
        │   └── Entity.tsx.j2
        └── vue/
            └── Entity.vue.j2
```

## Best Practices

1. **Documentation**: Always include comprehensive documentation
2. **Error Handling**: Gracefully handle and report errors
3. **Configuration**: Support configuration through `plugin.yaml`
4. **Dependencies**: Clearly specify dependencies and versions
5. **Testing**: Include tests for your plugin
6. **Type Hints**: Use Python type hints for better IDE support

## Plugin Registry

The official DomainForge plugin registry is available at `https://plugins.domain-forge.org`. To publish your plugin:

1. Package your plugin according to the structure above
2. Create a repository on GitHub
3. Submit a PR to the registry repository

## Examples

See the example plugins included with DomainForge:

- `default-validator`: Basic validation rules
- `example-template`: Template customization example
- `base-template`: Core templates

## Development Tips

### Testing Plugins Locally

1. Create a development environment:
```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e .
```

2. Install your plugin for testing:
```bash
domainforge plugins install ./my-plugin
```

3. Run plugin tests:
```bash
pytest tests/plugins/test_my_plugin.py
```

### Debugging

Enable debug logging for detailed information:

```bash
domainforge --log-level debug plugins install my-plugin
```

### Common Issues

1. **Plugin Not Found**: Check the plugins directory path
2. **Import Errors**: Verify dependencies are installed
3. **Template Errors**: Check template syntax and variables
4. **Version Conflicts**: Check dependency versions

## API Reference

### Plugin Interface

```python
class Plugin(ABC):
    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        pass

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the plugin."""
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Clean up plugin resources."""
        pass
```

### Validator Interface

```python
class ValidatorPlugin(Plugin):
    @abstractmethod
    def validate_model(self, model: str, strict: bool = False) -> ValidationResult:
        """Validate a domain model."""
        pass

    @abstractmethod
    def validate_file(self, file_path: str, strict: bool = False) -> ValidationResult:
        """Validate a domain model file."""
        pass
```

For more information and examples, visit the [DomainForge Documentation](https://domain-forge.readthedocs.io/plugins).
