# DomainForge CLI Documentation

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Command Structure](#command-structure)
4. [Global Options](#global-options)
5. [Commands](#commands)
   - [generate](#generate)
   - [init](#init)
   - [validate](#validate)
   - [plugins](#plugins)
6. [Configuration](#configuration)
7. [Environment Variables](#environment-variables)
8. [Exit Codes](#exit-codes)
9. [Examples](#examples)
10. [Troubleshooting](#troubleshooting)

## Overview

DomainForge CLI is a command-line tool for generating full-stack applications from domain model specifications using the DomainForge Domain-Specific Language (DSL). The CLI supports various commands for project initialization, code generation, validation, and plugin management.

## Installation

Install DomainForge using pip:

```bash
pip install domain-forge
```

Or install from source:

```bash
git clone https://github.com/yourusername/domain-forge.git
cd domain-forge
pip install -e .
```

## Command Structure

The CLI follows this general structure:

```bash
domainforge [global options] command [command options] [arguments]
```

## Global Options

- `--log-level`: Set logging level (debug, info, warning, error) [default: info]
- `--config`: Path to configuration file [default: ~/.domainforge/config.yaml]
- `--version`: Show version information
- `--help`: Show help message and exit

## Commands

### generate

Generate code from a DomainForge DSL file.

```bash
domainforge generate [options] <input-file>
```

#### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--output-dir`, `-o` | Output directory for generated code | Current directory |
| `--backend` | Backend framework to use | fastapi |
| `--frontend` | Frontend framework to use | react |
| `--template` | Template to use for generation | default |
| `--clean` | Clean output directory before generating | false |

#### Examples

```bash
# Generate from a DSL file
domainforge generate domain.df -o my-app

# Generate with specific frameworks
domainforge generate domain.df --backend fastapi --frontend react

# Generate using a custom template
domainforge generate domain.df --template custom-template
```

### init

Initialize a new DomainForge project.

```bash
domainforge init [options] <project-name>
```

#### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--template` | Template to use | default |
| `--backend` | Initial backend framework | fastapi |
| `--frontend` | Initial frontend framework | react |
| `--git/--no-git` | Initialize git repository | true |

#### Examples

```bash
# Create a new project
domainforge init my-project

# Create with specific frameworks
domainforge init my-project --backend fastapi --frontend react

# Create without git initialization
domainforge init my-project --no-git
```

### validate

Validate a DomainForge DSL file.

```bash
domainforge validate [options] <input-file>
```

#### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--strict` | Enable strict validation | false |
| `--format` | Output format (text, json) | text |

#### Examples

```bash
# Validate a DSL file
domainforge validate domain.df

# Validate with strict checks
domainforge validate domain.df --strict

# Validate with JSON output
domainforge validate domain.df --format json
```

### plugins

Manage DomainForge plugins.

```bash
domainforge plugins [command] [options]
```

#### Subcommands

| Command | Description | Example |
|---------|-------------|---------|
| `list` | List installed plugins | `plugins list` |
| `install` | Install a plugin | `plugins install my-plugin` |
| `uninstall` | Uninstall a plugin | `plugins uninstall my-plugin` |
| `update` | Update plugins | `plugins update` |

#### Examples

```bash
# List installed plugins
domainforge plugins list

# Install a plugin
domainforge plugins install my-plugin --version 1.0.0

# Uninstall a plugin
domainforge plugins uninstall my-plugin

# Update all plugins
domainforge plugins update
```

## Configuration

DomainForge can be configured using a configuration file or environment variables. The default configuration file location is `~/.domainforge/config.yaml`.

### Configuration File Structure

```yaml
# ~/.domainforge/config.yaml
plugins_dir: ~/.domainforge/plugins
templates_dir: ~/.domainforge/templates
default_backend: fastapi
default_frontend: react
plugin_registry: https://plugins.domainforge.org
template_registry: https://templates.domainforge.org
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DOMAINFORGE_CONFIG` | Path to config file | ~/.domainforge/config.yaml |
| `DOMAINFORGE_PLUGIN_PATH` | Plugin directory | ~/.domainforge/plugins |
| `DOMAINFORGE_TEMPLATES_DIR` | Templates directory | ~/.domainforge/templates |
| `DOMAINFORGE_LOG_LEVEL` | Logging level | info |

## Exit Codes

| Code | Description |
|------|-------------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid command usage |
| 3 | Invalid configuration |
| 4 | Plugin error |
| 5 | Generation error |
| 6 | Validation error |

## Examples

### Basic Project Generation

```bash
# Initialize a new project
domainforge init my-app

# Create a domain model
echo "@MyDomain { #User { name: String } }" > domain.df

# Generate the application
domainforge generate domain.df -o my-app
```

### Working with Plugins

```bash
# Install a custom template plugin
domainforge plugins install custom-template

# Generate using the custom template
domainforge generate domain.df --template custom-template

# List installed plugins
domainforge plugins list
```

### Advanced Usage

```bash
# Initialize with specific frameworks
domainforge init my-app --backend fastapi --frontend react

# Validate domain model
domainforge validate domain.df --strict

# Generate with clean output
domainforge generate domain.df --clean --output-dir my-app
```

## Troubleshooting

### Common Issues

1. **Plugin Installation Fails**
   - Check internet connection
   - Verify plugin name and version
   - Ensure write permissions in plugins directory

2. **Generation Errors**
   - Validate DSL file syntax
   - Check output directory permissions
   - Review framework compatibility

3. **Template Not Found**
   - Verify template installation
   - Check template name spelling
   - Ensure template compatibility with chosen frameworks

### Getting Help

- Run `domainforge --help` for general help
- Run `domainforge <command> --help` for command-specific help
- Visit the [documentation](https://domain-forge.readthedocs.io) for detailed guides
- Open issues on [GitHub](https://github.com/yourusername/domain-forge/issues)
