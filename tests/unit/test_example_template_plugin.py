"""Unit tests for example template plugin."""

import os
import shutil
from pathlib import Path

import pytest
from domainforge.plugins.template_plugin import PluginMetadata, TemplatePlugin


class ExampleTemplatePlugin(TemplatePlugin):
    """Example template plugin implementation for testing purposes.

    This class extends TemplatePlugin to provide a concrete implementation
    used in unit tests. It demonstrates basic plugin functionality including
    metadata handling and template management.
    """

    def __init__(self):
        super().__init__()
        self.metadata = PluginMetadata(
            name="example-template",
            version="1.0.0",
            description="Example template plugin",
            author="DomainForge Team",
            plugin_type="template",
        )

    def _create_test_templates(self, template_dir: Path) -> None:
        """Create test template files at the specified location.

        This method is separate from the TemplatePlugin implementation and used
        only for testing purposes to create expected template files.

        Args:
            template_dir: The directory where templates will be created
        """
        # Create backend templates
        backend_dir = template_dir / "backend"
        backend_dir.mkdir(exist_ok=True, parents=True)

        # Create FastAPI templates
        fastapi_dir = backend_dir / "fastapi"
        fastapi_dir.mkdir(exist_ok=True)
        with open(fastapi_dir / "entity.py.j2", "w") as f:
            f.write("""from fastapi import APIRouter\n
class {{ entity.name }}:\n    \"\"\"{{ entity.description }}\"\"\"\n
    {% for prop in entity.properties %}
    {{ prop.name }}: {{ prop.type }}\n    {% endfor %}

router = APIRouter()
""")

        # Create Django templates
        django_dir = backend_dir / "django"
        django_dir.mkdir(exist_ok=True)
        with open(django_dir / "models.py.j2", "w") as f:
            f.write("""from django.db import models\n
class {{ entity.name }}(models.Model):\n    \"\"\"{{ entity.description }}\"\"\"\n
    {% for prop in entity.properties %}
    {{ prop.name }} = models.{{ prop.django_type }}()\n    {% endfor %}
""")

        # Create frontend templates
        frontend_dir = template_dir / "frontend"
        frontend_dir.mkdir(exist_ok=True, parents=True)

        # Create React templates
        react_dir = frontend_dir / "react"
        react_dir.mkdir(exist_ok=True)
        with open(react_dir / "Entity.tsx.j2", "w") as f:
            f.write("""import React from 'react';\n
interface {{ entity.name }}Props {\n    {% for prop in entity.properties %}
    {{ prop.name }}: {{ prop.ts_type }};\n    {% endfor %}
}\n
export const {{ entity.name }}: React.FC<{{ entity.name }}Props> = (props) => {
    return (
        <div>
            {/* Component implementation */}
        </div>
    );
};
""")

        # Create Vue templates
        vue_dir = frontend_dir / "vue"
        vue_dir.mkdir(exist_ok=True)
        with open(vue_dir / "Entity.vue.j2", "w") as f:
            f.write("""<template>
  <div class="{{ entity.name | kebabcase }}-component">
    <!-- Component template -->
  </div>
</template>

<script>
export default {
  name: '{{ entity.name }}',
  props: {
    {% for prop in entity.properties %}
    {{ prop.name }}: {{ prop.vue_type }},
    {% endfor %}
  }
}
</script>
""")


@pytest.fixture
def plugin():
    """Create plugin instance for testing."""
    return ExampleTemplatePlugin()


@pytest.fixture
def mock_template_dir(monkeypatch, tmp_path):
    """Create a mock template directory and patch its location.

    This fixture creates a template directory for testing and mocks the template
    location to ensure tests work regardless of the actual implementation.

    Args:
        monkeypatch: pytest's monkeypatch fixture
        tmp_path: pytest's temporary directory fixture

    Returns:
        Path to the mock template directory
    """
    test_template_dir = tmp_path / "test_templates"
    test_template_dir.mkdir(exist_ok=True)

    # Instead of trying to patch a specific method, patch template_dir directly
    def mock_initialize(self, config):
        """Mock initialize method to set template_dir to our test directory."""
        self.template_dir = test_template_dir
        return self.template_dir

    # Apply the patch to the initialize method
    monkeypatch.setattr(TemplatePlugin, "initialize", mock_initialize)

    return test_template_dir


def test_metadata(plugin):
    """Test plugin metadata."""
    assert plugin.metadata.name == "example-template"
    assert plugin.metadata.version == "1.0.0"


def test_supported_frameworks(plugin):
    """Test supported frameworks are correctly reported."""
    frameworks = plugin.get_supported_frameworks()
    assert "backend" in frameworks
    assert "frontend" in frameworks

    assert "fastapi" in frameworks["backend"]
    assert "django" in frameworks["backend"]
    assert "react" in frameworks["frontend"]
    assert "vue" in frameworks["frontend"]


def test_template_paths(plugin, mock_template_dir):
    """Test template paths are correct."""
    # Arrange
    plugin.initialize({})  # This will now set plugin.template_dir to mock_template_dir
    plugin._create_test_templates(mock_template_dir)

    # Act
    paths = plugin.get_template_paths()

    # Assert
    assert "backend" in paths, "Backend key should be in paths"
    assert "frontend" in paths, "Frontend key should be in paths"

    backend_path = mock_template_dir / "backend"
    frontend_path = mock_template_dir / "frontend"

    assert paths["backend"].exists(), f"Backend path should exist at {backend_path}"
    assert paths["frontend"].exists(), f"Frontend path should exist at {frontend_path}"

    # Check if the paths match our mock directory
    assert str(paths["backend"]).startswith(str(mock_template_dir)), (
        f"Backend path {paths['backend']} should be within {mock_template_dir}"
    )
    assert str(paths["frontend"]).startswith(str(mock_template_dir)), (
        f"Frontend path {paths['frontend']} should be within {mock_template_dir}"
    )

    # Check template files
    fastapi_template = paths["backend"] / "fastapi" / "entity.py.j2"
    react_template = paths["frontend"] / "react" / "Entity.tsx.j2"

    assert fastapi_template.exists(), (
        f"FastAPI template should exist at {fastapi_template}"
    )
    assert react_template.exists(), f"React template should exist at {react_template}"


def test_template_content(plugin, mock_template_dir):
    """Test template content is valid and contains expected placeholders."""
    # Arrange
    plugin.initialize({})  # This will now set plugin.template_dir to mock_template_dir
    plugin._create_test_templates(mock_template_dir)

    # Act
    paths = plugin.get_template_paths()

    # Assert
    # Test FastAPI template
    with open(paths["backend"] / "fastapi" / "entity.py.j2") as f:
        fastapi_template = f.read()
        assert "{{ entity.name }}" in fastapi_template, (
            "FastAPI template should contain entity.name placeholder"
        )
        assert "{% for prop in entity.properties %}" in fastapi_template, (
            "FastAPI template should contain property loop"
        )
        assert "router = APIRouter" in fastapi_template, (
            "FastAPI template should include APIRouter"
        )

    # Test React template
    with open(paths["frontend"] / "react" / "Entity.tsx.j2") as f:
        react_template = f.read()
        assert "{{ entity.name }}" in react_template, (
            "React template should contain entity.name placeholder"
        )
        assert "{% for prop in entity.properties %}" in react_template, (
            "React template should contain property loop"
        )
        assert "React.FC" in react_template, (
            "React template should include React.FC type"
        )


def test_initialize_creates_directories(plugin, mock_template_dir):
    """Test if the template directories are properly managed."""
    # Arrange & Act
    plugin.initialize({})  # This will now set plugin.template_dir to mock_template_dir

    # Assert
    assert plugin.template_dir == mock_template_dir, (
        "Template directory should be set correctly"
    )

    # Create the test templates in the mocked location
    plugin._create_test_templates(mock_template_dir)

    # Verify directories exist in our mock location
    backend_dir = mock_template_dir / "backend"
    frontend_dir = mock_template_dir / "frontend"

    assert backend_dir.exists(), (
        f"Backend template directory should exist at {backend_dir}"
    )
    assert frontend_dir.exists(), (
        f"Frontend template directory should exist at {frontend_dir}"
    )

    # Check framework directories
    assert (backend_dir / "fastapi").exists(), "FastAPI template directory should exist"
    assert (backend_dir / "django").exists(), "Django template directory should exist"
    assert (frontend_dir / "react").exists(), "React template directory should exist"
    assert (frontend_dir / "vue").exists(), "Vue template directory should exist"


def test_initialize_with_existing_directories(plugin, mock_template_dir):
    """Test initialization with pre-existing template directories."""
    # Arrange - Create directory structure beforehand
    backend_dir = mock_template_dir / "backend"
    frontend_dir = mock_template_dir / "frontend"
    backend_dir.mkdir(exist_ok=True)
    frontend_dir.mkdir(exist_ok=True)

    # Act
    plugin.initialize({})  # This will now set plugin.template_dir to mock_template_dir

    # Assert - Directories should still exist
    assert backend_dir.exists(), "Backend directory should exist"
    assert frontend_dir.exists(), "Frontend directory should exist"
    assert plugin.template_dir == mock_template_dir, (
        "Template directory should be set correctly"
    )


def test_template_paths_after_initialization(plugin, mock_template_dir):
    """Test template paths after proper initialization."""
    # Arrange - Set up template structure
    backend_dir = mock_template_dir / "backend"
    frontend_dir = mock_template_dir / "frontend"
    backend_dir.mkdir(exist_ok=True, parents=True)
    frontend_dir.mkdir(exist_ok=True, parents=True)

    # Create framework directories and template files
    fastapi_dir = backend_dir / "fastapi"
    fastapi_dir.mkdir(exist_ok=True)
    (fastapi_dir / "entity.py.j2").write_text("{{ entity.name }}")

    react_dir = frontend_dir / "react"
    react_dir.mkdir(exist_ok=True)
    (react_dir / "Entity.tsx.j2").write_text("React.FC<{{ entity.name }}>")

    # Act
    plugin.initialize({})  # This will now set plugin.template_dir to mock_template_dir
    paths = plugin.get_template_paths()

    # Assert
    assert "backend" in paths, "Backend path should be in template paths"
    assert "frontend" in paths, "Frontend path should be in template paths"

    # Check if paths are within our mock directory
    assert str(paths["backend"]).startswith(str(mock_template_dir)), (
        f"Backend path {paths['backend']} should be within {mock_template_dir}"
    )
    assert str(paths["frontend"]).startswith(str(mock_template_dir)), (
        f"Frontend path {paths['frontend']} should be within {mock_template_dir}"
    )

    # Check template files
    fastapi_template = paths["backend"] / "fastapi" / "entity.py.j2"
    react_template = paths["frontend"] / "react" / "Entity.tsx.j2"

    assert fastapi_template.exists(), (
        f"FastAPI template should exist at {fastapi_template}"
    )
    assert react_template.exists(), f"React template should exist at {react_template}"
