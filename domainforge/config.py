import os


class Settings:
    """Configuration settings for DomainForge."""

    def __init__(self):
        """Initialize settings with default values."""
        self.plugins_dir = os.path.expanduser("~/.domainforge/plugins")
        self.plugin_registry = "https://registry.domainforge.io"  # Default registry URL
