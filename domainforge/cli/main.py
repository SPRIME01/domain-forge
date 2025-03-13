"""Main CLI module for DomainForge."""

import os
import click
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any

from domainforge.plugins import (
    Plugin,
    PluginManager,
    PluginNotFoundError,
    PluginType,
)
from domainforge.core import parse_domain_model, transform_model
from domainforge.config import get_settings
from domainforge.generators import (
    PythonBackendGenerator,
    TypeScriptFrontendGenerator,
    CodeGenerator,  
)


@click.group()
def app():
    """DomainForge CLI - Generate full-stack applications from domain models."""
    pass


@app.group()
def plugins():
    """Manage DomainForge plugins."""
    pass


@plugins.command("list")
@click.option("--type", "plugin_type", help="Filter plugins by type")
def list_plugins(plugin_type: Optional[str] = None):
    """List installed plugins."""
    settings = get_settings()
    manager = PluginManager(settings.plugins_dir)
    plugins = manager.list_plugins()

    if not plugins:
        click.echo("No plugins installed")
        return

    if plugin_type:
        try:
            type_enum = PluginType[plugin_type.upper()]
            plugins = [p for p in plugins if p.metadata.plugin_type == type_enum]
        except KeyError:
            click.echo(f"Invalid plugin type: {plugin_type}")
            return

    for plugin in plugins:
        meta = plugin.metadata
        click.echo(f"{meta.name} (v{meta.version})")
        click.echo(f"  Type: {meta.plugin_type.name.lower()}")
        click.echo(f"  Author: {meta.author}")
        click.echo(f"  Description: {meta.description}")
        click.echo()


@plugins.command()
@click.argument("plugin_name")
def uninstall(plugin_name: str):
    """Uninstall a plugin."""
    settings = get_settings()
    manager = PluginManager(settings.plugins_dir)

    try:
        manager.uninstall_plugin(plugin_name)
        click.echo(f"Uninstalled plugin: {plugin_name}")
    except PluginNotFoundError:
        click.echo(f"Plugin not found: {plugin_name}")
        return 1


@app.command()
@click.argument("model_file", type=click.Path(exists=True))
@click.option("--strict", is_flag=True, help="Enable strict validation")
@click.option(
    "--format", "output_format", type=click.Choice(["text", "json"]), default="text"
)
def validate(model_file: str, strict: bool = False, output_format: str = "text"):
    """Validate a domain model file."""
    settings = get_settings()
    manager = PluginManager(settings.plugins_dir)

    validator = manager.get_default_validator()
    if not validator:
        click.echo("No validator plugin found")
        return 1

    result = validator.validate_file(model_file, strict)

    if output_format == "json":
        import json

        output = {
            "valid": result.is_valid,
            "errors": result.errors,
            "warnings": result.warnings,
        }
        click.echo(json.dumps(output, indent=2))
    else:
        if result.is_valid:
            click.echo("Validation successful")
        else:
            click.echo("Validation Errors:")
            for error in result.errors:
                click.echo(f"- {error}")
            if result.warnings:
                click.echo("\nWarnings:")
                for warning in result.warnings:
                    click.echo(f"- {warning}")

    return 0 if result.is_valid else 1


@app.command()
@click.argument("model_file", type=click.Path(exists=True))
@click.option("--backend", type=str, help="Backend framework to use")
@click.option("--frontend", type=str, help="Frontend framework to use")
@click.option("--output-dir", type=click.Path(), default=".", help="Output directory")
def generate(
    model_file: str,
    backend: Optional[str] = None,
    frontend: Optional[str] = None,
    output_dir: str = ".",
):
    """Generate code from a domain model file."""
    settings = get_settings()
    manager = PluginManager(settings.plugins_dir)

    # Parse and validate model
    with open(model_file) as f:
        model_text = f.read()

    model = parse_domain_model(model_text)
    transformed = transform_model(model)

    generators: Dict[str, CodeGenerator] = {}

    if backend:
        if backend == "fastapi":
            generators["backend"] = PythonBackendGenerator()
        else:
            click.echo(f"Unsupported backend framework: {backend}")
            return 1

    if frontend:
        if frontend == "react":
            generators["frontend"] = TypeScriptFrontendGenerator()
        else:
            click.echo(f"Unsupported frontend framework: {frontend}")
            return 1

    output_path = Path(output_dir)
    for gen_type, generator in generators.items():
        generator.generate(transformed, output_path / gen_type)

    click.echo(f"Generated code in: {output_path}")
    return 0


def main():
    """Main entry point for the CLI."""
    app()
