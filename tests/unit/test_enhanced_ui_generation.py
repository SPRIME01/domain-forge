import pytest
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum

# Import mock models directly without relative import
from tests.unit.test_enhanced_ui_model import UIComponent, ComponentType, UIDefinition


@dataclass
class CodeGenerationResult:
    """Class representing the result of code generation."""

    typescript_code: str
    css_code: Optional[str] = None
    imports: List[str] = field(default_factory=list)


class UIComponentGenerator:
    """Mock generator that converts UI component models to React TypeScript code."""

    def generate_component(self, component: UIComponent) -> CodeGenerationResult:
        """Generate React component code from a UI component model."""
        component_type = component.component_type
        imports = []

        # Basic implementation to generate different code based on component type
        if component_type in [
            ComponentType.FORM,
            ComponentType.TABLE,
            ComponentType.CARD,
            ComponentType.DETAIL,
            ComponentType.LIST,
        ]:
            return self._generate_basic_component(component)

        elif component_type in [
            ComponentType.CONTAINER,
            ComponentType.GRID,
            ComponentType.FLEX,
            ComponentType.PANEL,
            ComponentType.TABS,
            ComponentType.ACCORDION,
        ]:
            return self._generate_layout_component(component)

        elif component_type in [
            ComponentType.MENU,
            ComponentType.NAVBAR,
            ComponentType.SIDEBAR,
            ComponentType.BREADCRUMBS,
            ComponentType.PAGINATION,
        ]:
            return self._generate_navigation_component(component)

        elif component_type in [
            ComponentType.INPUT,
            ComponentType.SELECT,
            ComponentType.CHECKBOX,
            ComponentType.RADIO,
            ComponentType.DATEPICKER,
            ComponentType.TIMEPICKER,
            ComponentType.FILEUPLOAD,
        ]:
            return self._generate_input_component(component)

        elif component_type in [
            ComponentType.MODAL,
            ComponentType.DIALOG,
            ComponentType.TOOLTIP,
            ComponentType.CHART,
            ComponentType.BADGE,
            ComponentType.AVATAR,
            ComponentType.PROGRESS,
        ]:
            return self._generate_display_component(component)

        else:
            # Default case
            return CodeGenerationResult(
                typescript_code=f"// Unknown component type: {component_type.value}"
            )

    def _generate_basic_component(self, component: UIComponent) -> CodeGenerationResult:
        """Generate code for basic components like Form, Table, etc."""
        component_name = f"{component.component_type.value}Component"
        props = self._generate_props(component.parameters)
        layout_style = self._generate_layout_style(component.layout)
        children_code = self._generate_children(component.children)

        code = f"""
import React from 'react';

interface {component_name}Props {{
  {props}
}}

export const {component_name}: React.FC<{component_name}Props> = (props) => {{
  return (
    <div className="{component.component_type.value.lower()}-component" style={{{layout_style}}}>
      {f"<h3>{component.description}</h3>" if component.description else ""}
      {children_code}
    </div>
  );
}};
"""

        return CodeGenerationResult(
            typescript_code=code.strip(), imports=["import React from 'react';"]
        )

    def _generate_layout_component(
        self, component: UIComponent
    ) -> CodeGenerationResult:
        """Generate code for layout components like Container, Grid, etc."""
        component_name = f"{component.component_type.value}Component"
        props = self._generate_props(component.parameters)
        layout_style = self._generate_layout_style(component.layout)
        children_code = self._generate_children(component.children)

        # Additional CSS for layout components
        css = f"""
.{component.component_type.value.lower()}-component {{
  display: flex;
  flex-direction: column;
  {f"max-width: {component.layout.get('maxWidth', '100%')};" if "maxWidth" in component.layout else ""}
  {f"margin: {component.layout.get('margin', '0')};" if "margin" in component.layout else ""}
}}
"""

        code = f"""
import React from 'react';
import './styles/{component.component_type.value.lower()}.css';

interface {component_name}Props {{
  {props}
  children?: React.ReactNode;
}}

export const {component_name}: React.FC<{component_name}Props> = (props) => {{
  return (
    <div className="{component.component_type.value.lower()}-component" style={{{layout_style}}}>
      {f"<h3>{component.description}</h3>" if component.description else ""}
      {children_code}
    </div>
  );
}};
"""

        return CodeGenerationResult(
            typescript_code=code.strip(),
            css_code=css.strip(),
            imports=[
                "import React from 'react';",
                f"import './styles/{component.component_type.value.lower()}.css';",
            ],
        )

    def _generate_navigation_component(
        self, component: UIComponent
    ) -> CodeGenerationResult:
        """Generate code for navigation components like Menu, Navbar, etc."""
        component_name = f"{component.component_type.value}Component"
        props = self._generate_props(component.parameters)
        layout_style = self._generate_layout_style(component.layout)
        children_code = self._generate_children(component.children)

        code = f"""
import React from 'react';
import {{ Link }} from 'react-router-dom';

interface {component_name}Props {{
  {props}
}}

export const {component_name}: React.FC<{component_name}Props> = (props) => {{
  return (
    <nav className="{component.component_type.value.lower()}-component" style={{{layout_style}}}>
      {f'<div className="nav-title">{component.description}</div>' if component.description else ""}
      {children_code}
    </nav>
  );
}};
"""

        return CodeGenerationResult(
            typescript_code=code.strip(),
            imports=[
                "import React from 'react';",
                "import { Link } from 'react-router-dom';",
            ],
        )

    def _generate_input_component(self, component: UIComponent) -> CodeGenerationResult:
        """Generate code for input components like Input, Select, etc."""
        component_name = f"{component.component_type.value}Component"
        props = self._generate_props(component.parameters)
        layout_style = self._generate_layout_style(component.layout)

        # For input components, handle specific input-related props
        input_type = component.parameters.get("type", "text")
        placeholder = component.parameters.get("placeholder", "")
        label = component.parameters.get("label", "")

        code = f"""
import React from 'react';

interface {component_name}Props {{
  {props}
  onChange?: (event: React.ChangeEvent<HTMLInputElement>) => void;
}}

export const {component_name}: React.FC<{component_name}Props> = (props) => {{
  return (
    <div className="{component.component_type.value.lower()}-wrapper" style={{{layout_style}}}>
      {f"<label>{label}</label>" if label else ""}
      <input
        type="{input_type}"
        className="{component.component_type.value.lower()}-component"
        placeholder="{placeholder}"
        {{...props}}
      />
      {f"<small>{component.description}</small>" if component.description else ""}
    </div>
  );
}};
"""

        return CodeGenerationResult(
            typescript_code=code.strip(), imports=["import React from 'react';"]
        )

    def _generate_display_component(
        self, component: UIComponent
    ) -> CodeGenerationResult:
        """Generate code for display components like Modal, Chart, etc."""
        component_name = f"{component.component_type.value}Component"
        props = self._generate_props(component.parameters)
        layout_style = self._generate_layout_style(component.layout)
        children_code = self._generate_children(component.children)

        code = f"""
import React from 'react';

interface {component_name}Props {{
  {props}
  isOpen?: boolean;
  onClose?: () => void;
}}

export const {component_name}: React.FC<{component_name}Props> = (props) => {{
  return (
    <div className="{component.component_type.value.lower()}-component" style={{{layout_style}}}>
      {f'<div className="component-header">{component.description}</div>' if component.description else ""}
      <div className="component-body">
        {children_code}
      </div>
      {f"<button onClick={{props.onClose}}>Close</button>" if component.component_type in [ComponentType.MODAL, ComponentType.DIALOG] else ""}
    </div>
  );
}};
"""

        return CodeGenerationResult(
            typescript_code=code.strip(), imports=["import React from 'react';"]
        )

    def _generate_props(self, parameters: Dict[str, Any]) -> str:
        """Generate TypeScript props from component parameters."""
        if not parameters:
            return ""

        props = []
        for name, value in parameters.items():
            # Skip special parameters that are handled separately
            if name in ["type", "placeholder", "label"]:
                continue

            # Simple implementation - in real code would handle types properly
            props.append(f"{name}: any;")

        return "\n  ".join(props)

    def _generate_layout_style(self, layout: Dict[str, Any]) -> str:
        """Generate inline style object from layout parameters."""
        if not layout:
            return "{}"

        styles = []
        for name, value in layout.items():
            # Convert camelCase to CSS kebab-case for style props
            css_name = "".join(
                ["-" + c.lower() if c.isupper() else c for c in name]
            ).lstrip("-")

            # Add the style property
            styles.append(f"{css_name}: '{value}'")

        return "{ " + ", ".join(styles) + " }"

    def _generate_children(self, children: List[UIComponent]) -> str:
        """Generate JSX for child components recursively."""
        if not children:
            return "{props.children}"

        # Generate child components recursively
        child_jsx = []
        for i, child in enumerate(children):
            component_name = f"{child.component_type.value}Component"
            child_props = self._generate_props(child.parameters)
            layout_style = self._generate_layout_style(child.layout)
            nested_children = self._generate_children(child.children)

            # Generate child component with its own children
            child_jsx.append(f'''
      <{component_name}
        {{...props}}
        style={{{layout_style}}}
        key="{i}"
      >
        {nested_children}
      </{component_name}>''')

        return "\n".join(child_jsx)


class TestEnhancedUIGeneration:
    """Test suite for enhanced UI component code generation."""

    @pytest.fixture
    def generator(self):
        """Fixture providing a UI component generator."""
        return UIComponentGenerator()

    def test_basic_component_generation(self, generator):
        """Test code generation for a basic component."""
        # Create a Form component
        form_component = UIComponent(
            component_type=ComponentType.FORM, description="User registration form"
        )

        # Generate code
        result = generator.generate_component(form_component)

        # Verify basic structure
        assert "FormComponent" in result.typescript_code
        assert "import React from 'react';" in result.imports
        assert "User registration form" in result.typescript_code

    def test_layout_component_with_style(self, generator):
        """Test code generation for a layout component with styles."""
        # Create a Container component with layout properties
        container_component = UIComponent(
            component_type=ComponentType.CONTAINER,
            layout={"maxWidth": "1200px", "margin": "0 auto"},
        )

        # Generate code
        result = generator.generate_component(container_component)

        # Verify layout styles
        assert "ContainerComponent" in result.typescript_code
        assert "max-width: '1200px'" in result.typescript_code
        assert "margin: '0 auto'" in result.typescript_code
        assert "import './styles/container.css';" in result.imports
        assert result.css_code is not None
        assert "max-width: 1200px;" in result.css_code

    def test_input_component_generation(self, generator):
        """Test code generation for an input component."""
        # Create an Input component
        input_component = UIComponent(
            component_type=ComponentType.INPUT,
            parameters={
                "type": "text",
                "placeholder": "Enter your name",
                "label": "Full Name",
            },
            description="Name input field",
        )

        # Generate code
        result = generator.generate_component(input_component)

        # Verify input specific code
        assert "InputComponent" in result.typescript_code
        assert 'type="text"' in result.typescript_code
        assert 'placeholder="Enter your name"' in result.typescript_code
        assert "<label>Full Name</label>" in result.typescript_code
        assert "Name input field" in result.typescript_code

    def test_nested_components_generation(self, generator):
        """Test code generation for nested components."""
        # Create a nested component structure
        form_component = UIComponent(
            component_type=ComponentType.FORM,
            children=[
                UIComponent(
                    component_type=ComponentType.INPUT, parameters={"label": "Username"}
                ),
                UIComponent(
                    component_type=ComponentType.INPUT,
                    parameters={"label": "Password", "type": "password"},
                ),
            ],
        )

        # Generate code
        result = generator.generate_component(form_component)

        # Verify components are referenced
        assert "FormComponent" in result.typescript_code
        assert "InputComponent" in result.typescript_code
        assert 'key="0"' in result.typescript_code
        assert 'key="1"' in result.typescript_code

    def test_complex_layout_generation(self, generator):
        """Test code generation for a complex layout."""
        # Create a complex nested structure
        container = UIComponent(
            component_type=ComponentType.CONTAINER,
            layout={"maxWidth": "1200px"},
            children=[
                UIComponent(
                    component_type=ComponentType.GRID,
                    parameters={"columns": 2},
                    children=[
                        UIComponent(
                            component_type=ComponentType.PANEL,
                            children=[
                                UIComponent(
                                    component_type=ComponentType.FORM,
                                    description="Contact Form",
                                )
                            ],
                        ),
                        UIComponent(
                            component_type=ComponentType.PANEL,
                            children=[
                                UIComponent(
                                    component_type=ComponentType.CHART,
                                    parameters={"type": "bar"},
                                )
                            ],
                        ),
                    ],
                )
            ],
        )

        # Generate code
        result = generator.generate_component(container)

        # Verify complex structure
        assert "ContainerComponent" in result.typescript_code
        assert "GridComponent" in result.typescript_code
        assert "PanelComponent" in result.typescript_code

    def test_navigation_component_generation(self, generator):
        """Test code generation for a navigation component."""
        # Create a Navbar component
        navbar = UIComponent(
            component_type=ComponentType.NAVBAR,
            parameters={"position": "fixed"},
            description="Main Navigation",
        )

        # Generate code
        result = generator.generate_component(navbar)

        # Verify navigation specifics
        assert "NavbarComponent" in result.typescript_code
        assert "<nav" in result.typescript_code
        assert "import { Link } from 'react-router-dom';" in result.imports
        assert "Main Navigation" in result.typescript_code
