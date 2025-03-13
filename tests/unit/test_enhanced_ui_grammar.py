import pytest
from lark import Lark, Token, Tree
from pathlib import Path
import os


@pytest.fixture
def enhanced_ui_parser():
    """Fixture providing a parser with enhanced UI component support."""
    # Use the actual grammar file from the project
    grammar_path = (
        Path(os.path.dirname(__file__)) / "../../domainforge/core/grammar.lark"
    )
    with open(grammar_path, "r") as f:
        grammar = f.read()

    return Lark(grammar, parser="lalr")


class TestEnhancedUIGrammar:
    """Test suite for enhanced UI component grammar features."""

    def test_basic_component_with_description(self, enhanced_ui_parser):
        """Test that basic components still work with the enhanced grammar."""
        dsl = """
        @Context {
            #Entity {
                ui: Form description: {
                    "A form for the entity"
                }
            }
        }
        """
        tree = enhanced_ui_parser.parse(dsl)

        # Verify context and entity structure
        context = tree.children[0]
        assert context.children[0] == Token("IDENTIFIER", "Context")

        entity = context.children[1].children[0]
        assert entity.children[0] == Token("IDENTIFIER", "Entity")

        # Verify UI component
        ui_def = entity.children[1].children[0]
        assert ui_def.data == "ui_definition"

        # UI component type should be "Form"
        ui_component = ui_def.children[0]
        assert ui_component == Token("BASIC_COMPONENT", "Form")

        # Check description
        ui_desc = ui_def.children[1]
        assert ui_desc.data == "ui_description"
        assert ui_desc.children[0].children[0] == Token(
            "STRING", '"A form for the entity"'
        )

    def test_nested_components(self, enhanced_ui_parser):
        """Test nesting UI components within each other."""
        dsl = """
        @Context {
            #Entity {
                ui: Container components: {
                    ui: Form description: {
                        "A nested form"
                    }
                    ui: Table description: {
                        "A nested table"
                    }
                }
            }
        }
        """
        tree = enhanced_ui_parser.parse(dsl)

        # Navigate to the UI definition
        context = tree.children[0]
        entity = context.children[1].children[0]
        container_ui = entity.children[1].children[0]

        # Verify Container component
        assert container_ui.data == "ui_definition"
        assert container_ui.children[0] == Token("LAYOUT_COMPONENT", "Container")

        # Verify children container and nested components
        ui_children = container_ui.children[1]
        assert ui_children.data == "ui_components"

        # First nested component should be Form
        form_ui = ui_children.children[0]
        assert form_ui.data == "ui_definition"
        assert form_ui.children[0] == Token("BASIC_COMPONENT", "Form")

        # Second nested component should be Table
        table_ui = ui_children.children[1]
        assert table_ui.data == "ui_definition"
        assert table_ui.children[0] == Token("BASIC_COMPONENT", "Table")

    def test_layout_parameters(self, enhanced_ui_parser):
        """Test UI components with layout parameters."""
        dsl = """
        @Context {
            #Entity {
                ui: Grid (
                    columns: 3,
                    gap: "1rem",
                    layout: {
                        justifyContent: "space-between"
                        alignItems: "center"
                    }
                ) components: {
                    ui: Card description: {
                        "First card"
                    }
                    ui: Card description: {
                        "Second card"
                    }
                }
            }
        }
        """
        tree = enhanced_ui_parser.parse(dsl)

        # Navigate to the UI definition
        context = tree.children[0]
        entity = context.children[1].children[0]
        grid_ui = entity.children[1].children[0]

        # Verify Grid component
        assert grid_ui.data == "ui_definition"
        assert grid_ui.children[0] == Token("LAYOUT_COMPONENT", "Grid")

        # Verify parameters
        params = grid_ui.children[1]
        assert params.data == "ui_params"

        param_list = params.children[0]
        assert param_list.data == "mixed_parameter_list"  # Updated assertion

        # Find the layout parameter definition within the mixed_parameter_list
        layout_param = None
        for child in param_list.children:
            if child.data == "layout_param_def":
                layout_param = child
                break

        # Ensure we found the layout parameter
        assert layout_param is not None, (
            "Layout parameter not found in mixed_parameter_list"
        )

        # Verify the layout object structure
        layout_object = layout_param.children[0]
        assert layout_object.data == "layout_object"

        # Check layout properties
        layout_props_list = layout_object.children[0]
        assert layout_props_list.data == "layout_property_list"

        layout_props = layout_props_list.children
        assert len(layout_props) == 2

        # Check specific layout properties
        justify_content = layout_props[0]
        assert justify_content.children[0] == Token("IDENTIFIER", "justifyContent")
        assert justify_content.children[1].data == "property_value"
        assert justify_content.children[1].children[0] == Token(
            "STRING", '"space-between"'
        )

        align_items = layout_props[1]
        assert align_items.children[0] == Token("IDENTIFIER", "alignItems")
        assert align_items.children[1].data == "property_value"
        assert align_items.children[1].children[0] == Token("STRING", '"center"')

    def test_navigation_components(self, enhanced_ui_parser):
        """Test navigation component types."""
        dsl = """
        @Context {
            #Entity {
                ui: Navbar (
                    position: "fixed",
                    brand: "MyApp"
                ) components: {
                    ui: Menu description: {
                        "Main navigation"
                    }
                }
            }
        }
        """
        tree = enhanced_ui_parser.parse(dsl)

        # Navigate to the UI definition
        context = tree.children[0]
        entity = context.children[1].children[0]
        navbar_ui = entity.children[1].children[0]

        # Verify Navbar component
        assert navbar_ui.data == "ui_definition"
        assert navbar_ui.children[0] == Token("NAV_COMPONENT", "Navbar")

        # Verify nested Menu component
        menu_ui = navbar_ui.children[2].children[0]
        assert menu_ui.data == "ui_definition"
        assert menu_ui.children[0] == Token("NAV_COMPONENT", "Menu")

    def test_input_components(self, enhanced_ui_parser):
        """Test input component types."""
        dsl = """
        @Context {
            #Entity {
                ui: Form components: {
                    ui: Input (
                        type: "text",
                        placeholder: "Enter your name"
                    ) description: {
                        "Name input field"
                    }
                    ui: Select (
                        options: ["Option 1", "Option 2"]
                    ) description: {
                        "Select dropdown"
                    }
                }
            }
        }
        """
        tree = enhanced_ui_parser.parse(dsl)

        # Navigate to Form UI definition
        context = tree.children[0]
        entity = context.children[1].children[0]
        form_ui = entity.children[1].children[0]

        # Verify Form component
        assert form_ui.data == "ui_definition"
        assert form_ui.children[0] == Token("BASIC_COMPONENT", "Form")

        # Verify Input component
        input_ui = form_ui.children[1].children[0]
        assert input_ui.data == "ui_definition"
        assert input_ui.children[0] == Token("INPUT_COMPONENT", "Input")

        # Verify Select component
        select_ui = form_ui.children[1].children[1]
        assert select_ui.data == "ui_definition"
        assert select_ui.children[0] == Token("INPUT_COMPONENT", "Select")

    def test_complex_nested_layout(self, enhanced_ui_parser):
        """Test a complex nested layout with multiple component types."""
        dsl = """
        @Context {
            #Entity {
                ui: Container (
                    layout: {
                        maxWidth: "1200px"
                        margin: "0 auto"
                    }
                ) components: {
                    ui: Grid (
                        columns: 2,
                        gap: "2rem"
                    ) components: {
                        ui: Panel components: {
                            ui: Form components: {
                                ui: Input (
                                    label: "Username"
                                ) description: {
                                    "Username input"
                                }
                                ui: Input (
                                    label: "Password",
                                    type: "password"
                                ) description: {
                                    "Password input"
                                }
                            }
                        }

                        ui: Panel components: {
                            ui: Chart (
                                type: "bar",
                                data: "chartData"
                            ) description: {
                                "User statistics"
                            }
                        }
                    }
                }
            }
        }
        """
        tree = enhanced_ui_parser.parse(dsl)

        # Navigate to Container
        context = tree.children[0]
        entity = context.children[1].children[0]
        container_ui = entity.children[1].children[0]

        # Verify Container component
        assert container_ui.data == "ui_definition"
        assert container_ui.children[0] == Token("LAYOUT_COMPONENT", "Container")

        # Check layout params
        layout_params = container_ui.children[1].children[0]
        assert layout_params.data == "mixed_parameter_list"  # Updated assertion

        # Navigate to Grid
        grid_ui = container_ui.children[2].children[0]
        assert grid_ui.data == "ui_definition"
        assert grid_ui.children[0] == Token("LAYOUT_COMPONENT", "Grid")

        # Navigate to Panels
        left_panel = grid_ui.children[2].children[0]
        assert left_panel.data == "ui_definition"
        assert left_panel.children[0] == Token("LAYOUT_COMPONENT", "Panel")

        right_panel = grid_ui.children[2].children[1]
        assert right_panel.data == "ui_definition"
        assert right_panel.children[0] == Token("LAYOUT_COMPONENT", "Panel")

        # Check Form in left panel
        form_ui = left_panel.children[1].children[0]
        assert form_ui.data == "ui_definition"
        assert form_ui.children[0] == Token("BASIC_COMPONENT", "Form")

        # Check Chart in right panel
        chart_ui = right_panel.children[1].children[0]
        assert chart_ui.data == "ui_definition"
        assert chart_ui.children[0] == Token("DISPLAY_COMPONENT", "Chart")


import pytest
from lark import Lark
from pathlib import Path
import os


@pytest.fixture
def grammar():
    """Load the grammar file for testing."""
    current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    grammar_path = current_dir / "../../domainforge/core/grammar.lark"

    with open(grammar_path, "r") as f:
        return f.read()


@pytest.fixture
def ui_parser(grammar):
    """Create a parser for UI component testing."""
    return Lark(grammar, start="ui_component")


def test_BasicComponent_WithProperties_ParsesSuccessfully(ui_parser):
    """Test that a basic component with properties can be parsed."""
    # Arrange
    input_text = """
    Card myCard {
        properties {
            title: "My Card"
            subtitle: "Card subtitle"
        }
    }
    """

    # Act
    result = ui_parser.parse(input_text)

    # Assert
    assert result is not None
    assert result.data == "ui_component"


def test_NestedComponents_WithChildren_ParsesSuccessfully(ui_parser):
    """Test that nested components with children can be parsed."""
    # Arrange
    input_text = """
    Page mainPage {
        properties {
            title: "Main Page"
        }
        children {
            Card card1 {
                properties {
                    title: "Child Card"
                }
            }
            Form loginForm {
                properties {
                    name: "login"
                }
            }
        }
    }
    """

    # Act
    result = ui_parser.parse(input_text)

    # Assert
    assert result is not None
    assert result.data == "ui_component"


def test_ComponentWithLayout_ParsesSuccessfully(ui_parser):
    """Test that a component with layout specification can be parsed."""
    # Arrange
    input_text = """
    Panel mainPanel {
        properties {
            title: "Main Panel"
        }
        layout {
            direction: "row"
            gap: 16
            align: "center"
            justify: "space-between"
        }
    }
    """

    # Act
    result = ui_parser.parse(input_text)

    # Assert
    assert result is not None
    assert result.data == "ui_component"


def test_NavigationFlow_BasicSyntax_ParsesSuccessfully(ui_parser):
    """Test that a component with navigation flow can be parsed."""
    # Arrange
    input_text = """
    Button submitButton {
        properties {
            label: "Submit"
        }
    } navigation {
        onClick -> HomePage
        onHover -> ShowTooltip("message": "Click to submit")
    }
    """

    # Act
    result = ui_parser.parse(input_text)

    # Assert
    assert result is not None
    assert result.data == "ui_component"


def test_ComplexComponent_WithAllFeatures_ParsesSuccessfully(ui_parser):
    """Test that a complex component with all features can be parsed."""
    # Arrange
    input_text = """
    Page dashboardPage {
        properties {
            title: "Dashboard"
            protected: true
        }
        layout {
            direction: "column"
            gap: 24
        }
        children {
            Navbar topNav {
                properties {
                    fixed: true
                }
            } navigation {
                onSelect -> NavigateTo("route": "/selected")
            }

            Panel mainContent {
                layout {
                    direction: "row"
                    wrap: true
                }
                children {
                    Card statsCard {
                        properties {
                            title: "Statistics"
                        }
                    }
                    Table dataTable {
                        properties {
                            paginated: true
                            rowsPerPage: 10
                        }
                    } navigation {
                        onRowClick -> ShowDetail("id": "rowId")
                    }
                }
            }
        }
    } navigation {
        onLoad -> FetchData("endpoint": "/api/dashboard")
        onBack -> HomePage
    }
    """

    # Act
    result = ui_parser.parse(input_text)

    # Assert
    assert result is not None
    assert result.data == "ui_component"
