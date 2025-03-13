"""Tests for plugin configuration management."""

import pytest
from pathlib import Path
from domainforge.plugins.config import PluginConfig, PluginConfigManager


@pytest.fixture
def config_file(tmp_path):
    """Create a temporary config file."""
    config_path = tmp_path / "plugins.yaml"
    return config_path


@pytest.fixture
def config_manager(config_file):
    """Create a config manager with temporary config file."""
    return PluginConfigManager(config_file)


def test_plugin_config_default_values():
    """Test default values for plugin config."""
    config = PluginConfig(name="test-plugin")
    assert config.enabled is True
    assert config.settings == {}


def test_get_config_creates_new_config(config_manager):
    """Test getting config for non-existent plugin creates new config."""
    config = config_manager.get_config("new-plugin")
    assert config.name == "new-plugin"
    assert config.enabled is True
    assert config.settings == {}


def test_update_config(config_manager):
    """Test updating plugin configuration."""
    config_manager.update_config("test-plugin", {"key": "value"})
    config = config_manager.get_config("test-plugin")
    assert config.settings["key"] == "value"


def test_enable_disable_plugin(config_manager):
    """Test enabling and disabling plugins."""
    config_manager.disable_plugin("test-plugin")
    assert not config_manager.is_plugin_enabled("test-plugin")

    config_manager.enable_plugin("test-plugin")
    assert config_manager.is_plugin_enabled("test-plugin")


def test_save_and_load_configs(config_manager, config_file):
    """Test saving and loading configurations."""
    # Setup initial config
    config_manager.update_config("test-plugin", {"key": "value"})
    config_manager.disable_plugin("test-plugin")

    # Create new manager to load saved config
    new_manager = PluginConfigManager(config_file)
    loaded_config = new_manager.get_config("test-plugin")

    assert loaded_config.name == "test-plugin"
    assert loaded_config.enabled is False
    assert loaded_config.settings["key"] == "value"


def test_multiple_plugins(config_manager):
    """Test managing multiple plugin configs."""
    # Configure first plugin
    config_manager.update_config("plugin1", {"setting1": "value1"})
    config_manager.disable_plugin("plugin1")

    # Configure second plugin
    config_manager.update_config("plugin2", {"setting2": "value2"})

    # Verify configurations
    config1 = config_manager.get_config("plugin1")
    assert config1.settings["setting1"] == "value1"
    assert not config1.enabled

    config2 = config_manager.get_config("plugin2")
    assert config2.settings["setting2"] == "value2"
    assert config2.enabled


def test_invalid_yaml_handling(tmp_path):
    """Test handling of invalid YAML config file."""
    config_path = tmp_path / "plugins.yaml"
    config_path.write_text("invalid: yaml: content")

    # Should not raise an exception
    manager = PluginConfigManager(config_path)
    assert isinstance(manager.get_config("test-plugin"), PluginConfig)
