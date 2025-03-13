"""Tests for the template loader functionality."""

import os
import pytest
from pathlib import Path

# Now the imports should match our implementation
from domainforge.plugins import Plugin, PluginMetadata, PluginType, PluginManager
from domainforge.plugins.template_plugin import TemplatePlugin


class MockTemplatePlugin(TemplatePlugin):
    """Mock template plugin implementation for testing."""

    def __init__(self):
        """Initialize the mock template plugin."""
        super().__init__()
        self.metadata = PluginMetadata(
            name="mock-template",
            version="1.0.0",
            description="Mock template plugin for testing",
            author="Test Author",
            plugin_type=PluginType.TEMPLATE,
        )


@pytest.fixture
def template_plugin():
    """Create a mock template plugin for testing."""
    return MockTemplatePlugin()


@pytest.fixture
def template_dir(tmp_path):
    """Create a temporary template directory with test templates."""
    # Create template directory structure
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()

    # Create backend templates
    backend_dir = templates_dir / "backend"
    backend_dir.mkdir()

    # Create FastAPI templates
    fastapi_dir = backend_dir / "fastapi"
    fastapi_dir.mkdir()

    with open(fastapi_dir / "entity.py.j2", "w") as f:
        f.write("class {{ entity.name }}:\n    pass")

    with open(fastapi_dir / "router.py.j2", "w") as f:
        f.write("from fastapi import APIRouter\nrouter = APIRouter()")

    # Create frontend templates
    frontend_dir = templates_dir / "frontend"
    frontend_dir.mkdir()

    # Create React templates
    react_dir = frontend_dir / "react"
    react_dir.mkdir()

    with open(react_dir / "Component.tsx.j2", "w") as f:
        f.write(
            "import React from 'react';\n\nexport const {{ entity.name }} = () => {\n  return <div>{{ entity.name }}</div>;\n};"
        )

    return templates_dir


def test_template_loader_finds_templates(template_plugin, template_dir):
    """Test that the template loader can find templates in the template directory."""
    # Initialize plugin with the template directory
    template_plugin.initialize({"template_dir": str(template_dir.parent)})

    # Get template paths
    paths = template_plugin.get_template_paths()

    # Check backend templates
    assert "backend" in paths
    backend_path = paths["backend"]
    assert backend_path.exists()

    # Check FastAPI templates
    fastapi_dir = backend_path / "fastapi"
    assert fastapi_dir.exists()
    assert (fastapi_dir / "entity.py.j2").exists()
    assert (fastapi_dir / "router.py.j2").exists()

    # Check frontend templates
    assert "frontend" in paths
    frontend_path = paths["frontend"]
    assert frontend_path.exists()

    # Check React templates
    react_dir = frontend_path / "react"
    assert react_dir.exists()
    assert (react_dir / "Component.tsx.j2").exists()


def test_template_loader_returns_correct_frameworks(template_plugin):
    """Test that the template loader returns the correct frameworks."""
    frameworks = template_plugin.get_supported_frameworks()

    # Check that the frameworks are correct
    assert "backend" in frameworks
    assert "frontend" in frameworks

    # Check backend frameworks
    backend_frameworks = frameworks["backend"]
    assert "fastapi" in backend_frameworks
    assert "django" in backend_frameworks

    # Check frontend frameworks
    frontend_frameworks = frameworks["frontend"]
    assert "react" in frontend_frameworks
    assert "vue" in frontend_frameworks


def test_template_loader_handles_missing_directory(template_plugin):
    """Test that the template loader handles missing directories gracefully."""
    # Initialize with a non-existent directory
    template_plugin.initialize({"template_dir": "/path/that/does/not/exist"})

    # Template dir should still be created
    assert template_plugin.template_dir.exists()

    # There should be no template paths yet
    paths = template_plugin.get_template_paths()
    assert len(paths) == 0


def test_template_loader_creates_directories(template_plugin, tmp_path):
    """Test that the template loader creates directories if they don't exist."""
    # Initialize with a temporary directory
    template_plugin.initialize({"template_dir": str(tmp_path)})

    # Template directory should exist
    assert template_plugin.template_dir.exists()
    assert template_plugin.template_dir == tmp_path / "templates"

    # No templates should be available yet
    paths = template_plugin.get_template_paths()
    assert len(paths) == 0

    # Create the template directories
    (template_plugin.template_dir / "backend").mkdir()
    (template_plugin.template_dir / "frontend").mkdir()

    # Now templates should be available
    paths = template_plugin.get_template_paths()
    assert "backend" in paths
    assert "frontend" in paths
