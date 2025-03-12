import pytest
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union, Any
from enum import Enum


# Mock domain models for testing
class ComponentType(Enum):
    """Enum representing UI component types."""

    # Basic Components
    FORM = "Form"
    TABLE = "Table"
    CARD = "Card"
    DETAIL = "Detail"
    LIST = "List"

    # Layout Components
    CONTAINER = "Container"
    GRID = "Grid"
    FLEX = "Flex"
    PANEL = "Panel"
    TABS = "Tabs"
    ACCORDION = "Accordion"

    # Navigation Components
    MENU = "Menu"
    NAVBAR = "Navbar"
    SIDEBAR = "Sidebar"
    BREADCRUMBS = "Breadcrumbs"
    PAGINATION = "Pagination"

    # Input Components
    INPUT = "Input"
    SELECT = "Select"
    CHECKBOX = "Checkbox"
    RADIO = "Radio"
    DATEPICKER = "DatePicker"
    TIMEPICKER = "TimePicker"
    FILEUPLOAD = "FileUpload"

    # Display Components
    MODAL = "Modal"
    DIALOG = "Dialog"
    TOOLTIP = "Tooltip"
    CHART = "Chart"
    BADGE = "Badge"
    AVATAR = "Avatar"
    PROGRESS = "Progress"


@dataclass
class UIComponent:
    """Base class for UI components in the domain model."""

    component_type: ComponentType
    parameters: Dict[str, Any] = field(default_factory=dict)
    layout: Dict[str, Any] = field(default_factory=dict)
    description: Optional[str] = None
    children: List["UIComponent"] = field(default_factory=list)


@dataclass
class UIDefinition:
    """Represents a UI component definition within an entity."""

    component: UIComponent


# Mock transformer for testing
class MockTransformer:
    """Mock transformer that converts DSL into domain models."""

    def transform_component_type(self, component_name: str) -> ComponentType:
        """Transform component name string into ComponentType enum."""
        return ComponentType(component_name)

    def transform_ui_definition(self, ui_def_tree) -> UIDefinition:
        """Transform UI definition tree into UIDefinition domain model."""
        # Simple example transformation - would be more complex in real implementation
        component_name = ui_def_tree.children[0].value
        component_type = self.transform_component_type(component_name)

        component = UIComponent(component_type=component_type)

        # Process parameters if present
        if (
            len(ui_def_tree.children) > 1
            and ui_def_tree.children[1].data == "ui_params"
        ):
            params_tree = ui_def_tree.children[1]
            component.parameters = self._extract_parameters(params_tree)

            # Process layout params if present
            for child in params_tree.children:
                if hasattr(child, "data") and child.data == "layout_params":
                    component.layout = self._extract_layout(child)

        # Process children if present
        children_index = -1
        for i, child in enumerate(ui_def_tree.children):
            if hasattr(child, "data") and child.data == "ui_children":
                children_index = i
                break

        if children_index >= 0:
            children_tree = ui_def_tree.children[children_index]
            for child_tree in children_tree.children:
                child_component = self.transform_ui_definition(child_tree)
                component.children.append(child_component.component)

        # Process description if present
        desc_index = -1
        for i, child in enumerate(ui_def_tree.children):
            if hasattr(child, "data") and child.data == "ui_desc":
                desc_index = i
                break

        if desc_index >= 0:
            desc_tree = ui_def_tree.children[desc_index]
            if (
                desc_tree.children
                and hasattr(desc_tree.children[0], "data")
                and desc_tree.children[0].data == "description"
            ):
                component.description = (
                    desc_tree.children[0].children[0].value.strip('"')
                )

        return UIDefinition(component=component)

    def _extract_parameters(self, params_tree) -> Dict[str, Any]:
        """Extract parameters from parameter list tree."""
        # Simplified parameter extraction for testing
        params = {}
        for child in params_tree.children:
            if hasattr(child, "data") and child.data == "parameter_list":
                for param in child.children:
                    name = param.children[0].value
                    # In real implementation, would extract and convert value
                    params[name] = "value"
        return params

    def _extract_layout(self, layout_tree) -> Dict[str, Any]:
        """Extract layout properties from layout tree."""
        # Simplified layout extraction for testing
        layout = {}
        for prop in layout_tree.children:
            name = prop.children[0].value
            # In real implementation, would extract and convert value
            layout[name] = "value"
        return layout


# Mock parser result tree for testing
@dataclass
class MockTree:
    """Mock Tree class to simulate Lark Tree structure."""

    data: str
    children: List[Any]


@dataclass
class MockToken:
    """Mock Token class to simulate Lark Token structure."""

    type: str
    value: str


class TestEnhancedUIModel:
    """Test suite for enhanced UI component model transformation."""

    @pytest.fixture
    def transformer(self):
        """Fixture providing a mock transformer."""
        return MockTransformer()

    def test_basic_component_transformation(self, transformer):
        """Test transformation of a basic UI component."""
        # Create a mock tree structure for a Form component
        mock_tree = MockTree(
            data="ui_definition",
            children=[
                MockToken(type="BASIC_COMPONENT", value="Form"),
                MockTree(
                    data="ui_desc",
                    children=[
                        MockTree(
                            data="description",
                            children=[
                                MockToken(type="STRING", value='"A simple form"')
                            ],
                        )
                    ],
                ),
            ],
        )

        # Transform the tree into a domain model
        ui_def = transformer.transform_ui_definition(mock_tree)

        # Verify the transformation
        assert isinstance(ui_def, UIDefinition)
        assert ui_def.component.component_type == ComponentType.FORM
        assert ui_def.component.description == "A simple form"
        assert len(ui_def.component.children) == 0

    def test_component_with_parameters(self, transformer):
        """Test transformation of a component with parameters."""
        # Create a mock tree structure for a Grid component with parameters
        mock_tree = MockTree(
            data="ui_definition",
            children=[
                MockToken(type="LAYOUT_COMPONENT", value="Grid"),
                MockTree(
                    data="ui_params",
                    children=[
                        MockTree(
                            data="parameter_list",
                            children=[
                                MockTree(
                                    data="parameter",
                                    children=[
                                        MockToken(type="IDENTIFIER", value="columns"),
                                        MockTree(
                                            data="type_definition", children=[]
                                        ),  # Simplified
                                        MockToken(type="INT", value="3"),  # Simplified
                                    ],
                                ),
                                MockTree(
                                    data="parameter",
                                    children=[
                                        MockToken(type="IDENTIFIER", value="gap"),
                                        MockTree(
                                            data="type_definition", children=[]
                                        ),  # Simplified
                                        MockToken(
                                            type="STRING", value='"1rem"'
                                        ),  # Simplified
                                    ],
                                ),
                            ],
                        )
                    ],
                ),
            ],
        )

        # Transform the tree into a domain model
        ui_def = transformer.transform_ui_definition(mock_tree)

        # Verify the transformation
        assert isinstance(ui_def, UIDefinition)
        assert ui_def.component.component_type == ComponentType.GRID
        assert "columns" in ui_def.component.parameters
        assert "gap" in ui_def.component.parameters

    def test_component_with_layout(self, transformer):
        """Test transformation of a component with layout parameters."""
        # Create a mock tree structure for a Container with layout
        mock_tree = MockTree(
            data="ui_definition",
            children=[
                MockToken(type="LAYOUT_COMPONENT", value="Container"),
                MockTree(
                    data="ui_params",
                    children=[
                        MockTree(data="parameter_list", children=[]),
                        MockTree(
                            data="layout_params",
                            children=[
                                MockTree(
                                    data="layout_property",
                                    children=[
                                        MockToken(type="IDENTIFIER", value="maxWidth"),
                                        MockTree(
                                            data="layout_value",
                                            children=[
                                                MockToken(
                                                    type="STRING", value='"1200px"'
                                                )
                                            ],
                                        ),
                                    ],
                                ),
                                MockTree(
                                    data="layout_property",
                                    children=[
                                        MockToken(type="IDENTIFIER", value="margin"),
                                        MockTree(
                                            data="layout_value",
                                            children=[
                                                MockToken(
                                                    type="STRING", value='"0 auto"'
                                                )
                                            ],
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        )

        # Transform the tree into a domain model
        ui_def = transformer.transform_ui_definition(mock_tree)

        # Verify the transformation
        assert isinstance(ui_def, UIDefinition)
        assert ui_def.component.component_type == ComponentType.CONTAINER
        assert "maxWidth" in ui_def.component.layout
        assert "margin" in ui_def.component.layout

    def test_nested_components(self, transformer):
        """Test transformation of nested components."""
        # Create a mock tree structure for a Container with nested Form
        mock_tree = MockTree(
            data="ui_definition",
            children=[
                MockToken(type="LAYOUT_COMPONENT", value="Container"),
                MockTree(
                    data="ui_children",
                    children=[
                        MockTree(
                            data="ui_definition",
                            children=[
                                MockToken(type="BASIC_COMPONENT", value="Form"),
                                MockTree(
                                    data="ui_desc",
                                    children=[
                                        MockTree(
                                            data="description",
                                            children=[
                                                MockToken(
                                                    type="STRING",
                                                    value='"A nested form"',
                                                )
                                            ],
                                        )
                                    ],
                                ),
                            ],
                        )
                    ],
                ),
            ],
        )

        # Transform the tree into a domain model
        ui_def = transformer.transform_ui_definition(mock_tree)

        # Verify the transformation
        assert isinstance(ui_def, UIDefinition)
        assert ui_def.component.component_type == ComponentType.CONTAINER
        assert len(ui_def.component.children) == 1

        child = ui_def.component.children[0]
        assert child.component_type == ComponentType.FORM
        assert child.description == "A nested form"

    def test_complex_component_hierarchy(self, transformer):
        """Test transformation of a complex component hierarchy."""
        # Create a mock tree structure for a complex UI hierarchy
        # Container > Grid > Panel > Form > Input
        container_mock = MockTree(
            data="ui_definition",
            children=[
                MockToken(type="LAYOUT_COMPONENT", value="Container"),
                MockTree(
                    data="ui_children",
                    children=[
                        MockTree(
                            data="ui_definition",
                            children=[
                                MockToken(type="LAYOUT_COMPONENT", value="Grid"),
                                MockTree(
                                    data="ui_children",
                                    children=[
                                        MockTree(
                                            data="ui_definition",
                                            children=[
                                                MockToken(
                                                    type="LAYOUT_COMPONENT",
                                                    value="Panel",
                                                ),
                                                MockTree(
                                                    data="ui_children",
                                                    children=[
                                                        MockTree(
                                                            data="ui_definition",
                                                            children=[
                                                                MockToken(
                                                                    type="BASIC_COMPONENT",
                                                                    value="Form",
                                                                ),
                                                                MockTree(
                                                                    data="ui_children",
                                                                    children=[
                                                                        MockTree(
                                                                            data="ui_definition",
                                                                            children=[
                                                                                MockToken(
                                                                                    type="INPUT_COMPONENT",
                                                                                    value="Input",
                                                                                ),
                                                                                MockTree(
                                                                                    data="ui_desc",
                                                                                    children=[
                                                                                        MockTree(
                                                                                            data="description",
                                                                                            children=[
                                                                                                MockToken(
                                                                                                    type="STRING",
                                                                                                    value='"Username field"',
                                                                                                )
                                                                                            ],
                                                                                        )
                                                                                    ],
                                                                                ),
                                                                            ],
                                                                        )
                                                                    ],
                                                                ),
                                                            ],
                                                        )
                                                    ],
                                                ),
                                            ],
                                        )
                                    ],
                                ),
                            ],
                        )
                    ],
                ),
            ],
        )

        # Transform the tree into a domain model
        ui_def = transformer.transform_ui_definition(container_mock)

        # Verify the transformation
        assert isinstance(ui_def, UIDefinition)
        assert ui_def.component.component_type == ComponentType.CONTAINER

        # Check the component hierarchy
        grid = ui_def.component.children[0]
        assert grid.component_type == ComponentType.GRID

        panel = grid.children[0]
        assert panel.component_type == ComponentType.PANEL

        form = panel.children[0]
        assert form.component_type == ComponentType.FORM

        input_comp = form.children[0]
        assert input_comp.component_type == ComponentType.INPUT
        assert input_comp.description == "Username field"
