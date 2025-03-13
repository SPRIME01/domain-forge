"""Click command integration for plugins."""

from typing import Any, Callable, Optional, Type
import click


def plugin_command(
    name: Optional[str] = None, cls: Optional[Type[click.Command]] = None, **attrs: Any
) -> Callable:
    """Create a Click command that can be added to the plugin group.

    This decorator ensures proper command registration with Click's command system.
    """

    def decorator(f: Callable) -> click.Command:
        # Ensure the command is properly registered with Click
        cmd = click.command(name=name, cls=cls, **attrs)(f)
        cmd._add_completion = lambda _: None  # type: ignore
        return cmd

    return decorator
