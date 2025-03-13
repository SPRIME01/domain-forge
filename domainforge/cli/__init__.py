"""DomainForge CLI package."""

import json
import yaml
from pathlib import Path
import click
from typing import Optional
from domainforge.plugins.discovery import find_plugins
from domainforge.config.settings import get_settings


@click.group()
def cli():
    """DomainForge CLI tool."""
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
    plugins = find_plugins()

    if not plugins:
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

    with open(input_file, "r") as f:
        model = f.read()

    all_errors = []
    for plugin in plugins:
        try:
            errors = plugin.validate(model)
            if errors:
                all_errors.extend(errors)
        except Exception as e:
            all_errors.append(str(e))

    has_errors = len(all_errors) > 0

    # Split errors into style suggestions and critical errors
    style_suggestions = [err for err in all_errors if "should be" in err]
    critical_errors = [err for err in all_errors if "should be" not in err]

    # In strict mode, any error makes the model invalid
    # In non-strict mode, only critical errors make the model invalid
    if strict:
        is_valid = not has_errors
    else:
        is_valid = len(critical_errors) == 0

    if output_format == "json":
        click.echo(
            json.dumps({"valid": is_valid, "errors": all_errors, "warnings": []})
        )
    else:
        if not has_errors:
            click.echo("Validation successful")
        else:
            click.echo("Validation Errors:")
            for error in all_errors:
                click.echo(f"- {error}")

    exit(0 if is_valid else 1)


@cli.group()
def plugins():
    """Plugin management commands."""
    pass


@plugins.command(name="list")
def list_plugins():
    """List installed plugins."""
    settings = get_settings()
    plugins_dir = Path(settings.plugins_dir)

    if not plugins_dir.exists() or not any(plugins_dir.iterdir()):
        click.echo("No plugins installed")
        return

    for plugin_dir in plugins_dir.iterdir():
        if not plugin_dir.is_dir():
            continue

        yaml_file = plugin_dir / "plugin.yaml"
        if yaml_file.exists():
            with open(yaml_file) as f:
                try:
                    info = yaml.safe_load(f)
                    click.echo(
                        f"{info['name']} v{info['version']} - {info['description']}"
                    )
                except Exception:
                    continue


@plugins.command()
@click.argument("name")
def uninstall(name: str):
    """Uninstall a plugin."""
    settings = get_settings()
    plugins_dir = Path(settings.plugins_dir)
    plugin_dir = plugins_dir / name

    if not plugin_dir.exists():
        click.echo(f"Plugin '{name}' is not installed")
        exit(1)

    import shutil

    shutil.rmtree(plugin_dir)
    click.echo(f"Uninstalled plugin '{name}'")


@plugins.command()
def update():
    """Update installed plugins."""
    settings = get_settings()
    plugins_dir = Path(settings.plugins_dir)

    if not plugins_dir.exists() or not any(plugins_dir.iterdir()):
        click.echo("No plugins installed")
        return

    click.echo("Plugin updates are not yet implemented")
    exit(0)


if __name__ == "__main__":
    cli()
