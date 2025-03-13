"""Command-line interface for DomainForge."""

import json
import logging
from pathlib import Path
import click
import yaml

from .config.settings import get_settings
from .plugins.plugin_manager import PluginManager
from .plugins.command import plugin_command
from .plugins.discovery import find_plugins

logger = logging.getLogger(__name__)

# Initialize the plugin manager
settings = get_settings()
plugin_manager = PluginManager(settings.plugins_dir)


def _handle_no_plugins(output_format: str) -> None:
    """Handle the case when no plugins are found."""
    if output_format == "json":
        click.echo(
            json.dumps(
                {
                    "valid": False,
                    "errors": ["No validator plugin found"],
                    "warnings": [],
                }
            )
        )
    else:
        click.echo("No validator plugin found")
    exit(1)


def _validate_with_plugins(model: str, plugins: list) -> tuple[list, list]:
    """Run validation using all plugins and return critical and style errors."""
    style_errors = []
    critical_errors = []

    for plugin in plugins:
        try:
            errors = plugin.validate(model)
            if errors:
                for error in errors:
                    if "should be" in error:
                        style_errors.append(error)
                    else:
                        critical_errors.append(error)
        except Exception as e:
            logger.exception("Plugin validation failed")
            critical_errors.append(str(e))

    return critical_errors, style_errors


def _output_validation_results(
    is_valid: bool,
    all_errors: list,
    output_format: str,
) -> None:
    """Output validation results in the specified format."""
    if output_format == "json":
        click.echo(
            json.dumps(
                {
                    "valid": is_valid,
                    "errors": all_errors,
                    "warnings": [],
                }
            )
        )
    else:
        if not all_errors:
            click.echo("Validation successful")
        else:
            click.echo("Validation Errors:")
            for error in all_errors:
                click.echo(f"- {error}")


@click.group()
def cli():
    """DomainForge CLI - Generate full-stack applications from domain models."""
    pass


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--strict", is_flag=True, help="Enable strict validation")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format",
)
def validate(input_file: str, strict: bool, output_format: str):
    """Validate a DomainForge DSL file."""
    # Use plugin manager for validation
    plugins = list(plugin_manager.plugins.values())
    if not plugins:
        _handle_no_plugins(output_format)

    with open(input_file, "r") as f:
        model = f.read()

    critical_errors, style_errors = _validate_with_plugins(model, plugins)

    # In strict mode, any error makes it invalid
    # In non-strict mode, only critical errors make it invalid
    is_valid = len(critical_errors) == 0 and (not strict or len(style_errors) == 0)

    all_errors = critical_errors + style_errors
    _output_validation_results(is_valid, all_errors, output_format)
    exit(0 if is_valid else 1)


@cli.group()
def plugins():
    """Plugin management commands."""
    pass


@plugin_command(name="list")
@plugins.command()
def list_plugins():
    """List installed plugins."""
    plugin_names = plugin_manager.list_plugins()

    if not plugin_names:
        click.echo("No plugins installed")
        return

    # Display plugin info
    for name in plugin_names:
        plugin = plugin_manager.get_plugin(name)
        if plugin and plugin.metadata:
            click.echo(
                f"{plugin.metadata.name} v{plugin.metadata.version} - {plugin.metadata.description}"
            )


@plugin_command()
@plugins.command()
@click.argument("name")
@click.option(
    "--source",
    type=click.Path(exists=True),
    help="Source directory containing plugin files",
)
def install(name: str, source: str):
    """Install a plugin."""
    try:
        plugin_manager.install_plugin(name, Path(source) if source else Path())
        click.echo(f"Installed plugin '{name}'")
    except Exception as e:
        click.echo(f"Failed to install plugin: {e}", err=True)
        exit(1)


@plugin_command()
@plugins.command()
@click.argument("name")
def uninstall(name: str):
    """Uninstall a plugin."""
    try:
        plugin_manager.uninstall_plugin(name)
        click.echo(f"Uninstalled plugin '{name}'")
    except Exception as e:
        click.echo(f"Failed to uninstall plugin: {e}", err=True)
        exit(1)


@plugin_command()
@plugins.command()
def templates():
    """List available templates from installed plugins."""
    plugin_names = plugin_manager.list_plugins()

    if not plugin_names:
        click.echo("No template plugins installed")
        return

    for name in plugin_names:
        plugin = plugin_manager.get_plugin(name)
        if not plugin:
            continue

        click.echo(f"\n{plugin.metadata.name}:")
        frameworks = plugin.get_supported_frameworks()
        for layer, supported in frameworks.items():
            click.echo(f"  {layer}:")
            for framework in supported:
                template_path = plugin.get_template_paths()[layer] / framework
                if template_path.exists():
                    templates = list(template_path.glob("*.j2"))
                    template_names = [t.name for t in templates]
                    if template_names:
                        click.echo(f"    {framework}: {', '.join(template_names)}")


if __name__ == "__main__":
    cli()
