"""Integration tests for the plugin system."""

import os
import sys
from pathlib import Path

import pytest

from domainforge.plugins.plugin_manager import PluginManager
from tests.integration.mock_plugin import MockPlugin


@pytest.fixture
def plugin_manager():
    """Create a plugin manager instance for testing."""
    manager = PluginManager()

    # Register mock plugin directly for testing
    mock_plugin = MockPlugin()
    manager.register_plugin(mock_plugin)

    return manager


def test_plugin_manager_loads_plugins(plugin_manager):
    """Test that the plugin manager can load plugins."""
    plugins = plugin_manager.get_plugins()
    assert "mock-plugin" in plugins
    assert plugins["mock-plugin"].metadata.name == "mock-plugin"


def test_plugin_manager_get_plugins_by_type(plugin_manager):
    """Test getting plugins by type."""
    test_plugins = plugin_manager.get_plugins_by_type("test")
    assert "mock-plugin" in test_plugins

    # No template plugins should be returned
    template_plugins = plugin_manager.get_plugins_by_type("template")
    assert len(template_plugins) == 0


def test_plugin_manager_uninstall(plugin_manager):
    """Test uninstalling a plugin."""
    # Verify plugin exists before uninstall
    plugins = plugin_manager.get_plugins()
    assert "mock-plugin" in plugins

    # Uninstall the plugin
    result = plugin_manager.uninstall("mock-plugin")
    assert result is True

    # Verify plugin no longer exists
    plugins = plugin_manager.get_plugins()
    assert "mock-plugin" not in plugins

    # Try to uninstall again (should fail gracefully)
    result = plugin_manager.uninstall("mock-plugin")
    assert result is False
