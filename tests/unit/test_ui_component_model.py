import pytest
from domainforge.domain.models.ui_component import (
    UIComponent,
    ComponentType,
    LayoutProperties,
    LayoutDirection,
    NavigationRule,
)


class TestUIComponentModel:
    @pytest.fixture
    def basic_component(self):
        """Create a basic UI component for testing."""
        return UIComponent(
            component_type=ComponentType.CARD,
            name="testCard",
            properties={"title": "Test Card", "subtitle": "A Test Card"},
        )

    @pytest.fixture
    def layout_properties(self):
        """Create layout properties for testing."""
        return LayoutProperties(
            direction=LayoutDirection.COLUMN,
            gap=16,
            align="center",
            justify="space-between",
        )

    @pytest.fixture
    def component_with_layout(self, basic_component, layout_properties):
        """Create a component with layout for testing."""
        component = basic_component
        component.layout = layout_properties
        return component

    @pytest.fixture
    def component_with_children(self, basic_component):
        """Create a component with children for testing."""
        child1 = UIComponent(
            component_type=ComponentType.BUTTON,  # Changed from CARD to BUTTON
            name="submitButton",
            properties={"label": "Submit"},
        )
        child2 = UIComponent(
            component_type=ComponentType.BUTTON,  # Changed from CARD to BUTTON
            name="cancelButton",
            properties={"label": "Cancel"},
        )

        component = basic_component
        component.add_child(child1)
        component.add_child(child2)
        return component

    def test_UIComponent_WithBasicProperties_CreatesCorrectly(self, basic_component):
        """Test that a UI component with basic properties is created correctly."""
        # Assert
        assert basic_component.component_type == ComponentType.CARD
        assert basic_component.name == "testCard"
        assert basic_component.properties["title"] == "Test Card"
        assert basic_component.properties["subtitle"] == "A Test Card"
        assert basic_component.has_children is False
        assert basic_component.has_navigation is False

    def test_UIComponent_WithLayoutProperties_IncludesLayoutInOutput(
        self, component_with_layout
    ):
        """Test that layout properties are included in the component's dictionary representation."""
        # Act
        result_dict = component_with_layout.to_dict()

        # Assert
        assert result_dict["layout"] is not None
        assert result_dict["layout"]["direction"] == LayoutDirection.COLUMN.value
        assert result_dict["layout"]["gap"] == 16
        assert result_dict["layout"]["align"] == "center"
        assert result_dict["layout"]["justify"] == "space-between"

    def test_UIComponent_WithChildren_ReportsChildrenCorrectly(
        self, component_with_children
    ):
        """Test that a component with children correctly reports its children."""
        # Assert
        assert component_with_children.has_children is True
        assert len(component_with_children.children) == 2
        assert component_with_children.children[0].name == "submitButton"
        assert component_with_children.children[1].name == "cancelButton"

    def test_AddChild_AddsChildCorrectly(self, basic_component):
        """Test that adding a child works correctly."""
        # Arrange
        child = UIComponent(
            component_type=ComponentType.TEXT,  # Changed from CARD to TEXT
            name="description",
            properties={"content": "This is a description"},
        )

        # Act
        basic_component.add_child(child)

        # Assert
        assert basic_component.has_children is True
        assert len(basic_component.children) == 1
        assert basic_component.children[0].name == "description"

    def test_AddNavigationRule_AddsRuleCorrectly(self, basic_component):
        """Test that adding a navigation rule works correctly."""
        # Act
        basic_component.add_navigation_rule("onClick", "DetailPage", {"id": "123"})

        # Assert
        assert basic_component.has_navigation is True
        assert len(basic_component.navigation_rules) == 1
        assert basic_component.navigation_rules[0].event == "onClick"
        assert basic_component.navigation_rules[0].target == "DetailPage"
        assert basic_component.navigation_rules[0].params == {"id": "123"}

    def test_ToDict_WithNavigationRules_IncludesRulesInOutput(self, basic_component):
        """Test that navigation rules are included in the component's dictionary representation."""
        # Arrange
        basic_component.add_navigation_rule("onClick", "DetailPage", {"id": "123"})
        basic_component.add_navigation_rule("onLoad", "FetchData")

        # Act
        result_dict = basic_component.to_dict()

        # Assert
        assert "navigation" in result_dict
        assert len(result_dict["navigation"]) == 2
        assert result_dict["navigation"][0]["event"] == "onClick"
        assert result_dict["navigation"][0]["target"] == "DetailPage"
        assert result_dict["navigation"][0]["params"] == {"id": "123"}
        assert result_dict["navigation"][1]["event"] == "onLoad"
        assert result_dict["navigation"][1]["target"] == "FetchData"
