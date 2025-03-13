"""Unit tests for DomainForgeParser's navigation flow processing."""

import pytest
from unittest.mock import MagicMock, patch
from domainforge.core.parser import DomainForgeParser


class TestParserNavigationFlow:
    """Tests navigation flow processing in DomainForgeParser."""

    @pytest.fixture
    def mock_transformer(self):
        """Create a mock transformer for testing."""
        transformer = MagicMock()
        return transformer

    @pytest.fixture
    def parser_with_mock(self, mock_transformer):
        """Create a parser with a mock transformer."""
        parser = DomainForgeParser()
        parser.transformer = mock_transformer
        return parser

    def test_process_navigation_flow_with_valid_rules_creates_navigation_rules(self):
        """Test that navigation flow rules are processed correctly."""
        # Arrange
        parser = DomainForgeParser()
        component = MagicMock()
        component.navigation_flow = [
            {"event": "onClick", "target": "HomePage", "params": {}},
            {"event": "onSubmit", "target": "SuccessPage", "params": {"id": "formId"}},
        ]

        # Act
        parser._process_navigation_flow(component)

        # Assert
        assert hasattr(component, "navigation_rules")
        assert len(component.navigation_rules) == 2
        assert component.navigation_rules[0]["event"] == "onClick"
        assert component.navigation_rules[0]["target"] == "HomePage"
        assert component.navigation_rules[1]["event"] == "onSubmit"
        assert component.navigation_rules[1]["target"] == "SuccessPage"
        assert component.navigation_rules[1]["params"] == {"id": "formId"}

    def test_process_nested_components_with_nested_navigation_processes_all_levels(
        self,
    ):
        """Test that nested components with navigation are processed correctly."""
        # Arrange
        parser = DomainForgeParser()

        # Create a mock child component with navigation flow
        child = MagicMock()
        child.navigation_flow = [
            {"event": "onClick", "target": "DetailPage", "params": {}}
        ]
        child.children = []

        # Create a mock parent component with navigation flow and a child
        parent = MagicMock()
        parent.navigation_flow = [
            {"event": "onLoad", "target": "FetchData", "params": {}}
        ]
        parent.children = [child]

        # Act
        # Mock the _process_navigation_flow method to track calls
        original_method = parser._process_navigation_flow
        calls = []

        def mock_process_nav(component):
            calls.append(component)
            return original_method(component)

        parser._process_navigation_flow = mock_process_nav
        parser._process_nested_components(parent)

        # Assert
        assert len(calls) == 2  # Should be called for parent and child
        assert calls[0] == child  # First call should be for the child component

    @patch("domainforge.core.parser.DomainForgeParser.parse")
    @patch("domainforge.core.parser.DomainForgeParser._process_navigation_flow")
    @patch("domainforge.core.parser.DomainForgeParser._process_nested_components")
    def test_parse_ui_components_processes_navigation_and_nesting(
        self, mock_process_nested, mock_process_nav, mock_parse, parser_with_mock
    ):
        """Test that parse_ui_components processes both navigation and nesting."""
        # Arrange
        mock_component = MagicMock()
        mock_component.navigation_flow = [{"event": "onClick", "target": "HomePage"}]
        mock_component.children = []

        # Create a complete successful parse result
        parse_result = MagicMock(spec=object)
        parse_result.ui_components = [mock_component]
        parse_result.success = True
        parse_result.error = None

        # Configure parse mock to handle any args and not raise exceptions
        mock_parse.return_value = parse_result
        mock_parse.side_effect = None

        # Ensure transformer is properly configured
        mock_transform_result = {"ui_components": [mock_component]}
        parser_with_mock.transformer.transform.return_value = mock_transform_result

        # Act
        result = parser_with_mock.parse_ui_components(
            "@Context { #Entity { ui: Form() } }"
        )

        # Assert
        assert result is not None
        assert "ui_components" in result
        mock_process_nav.assert_called_once_with(mock_component)
        mock_process_nested.assert_called_once_with(mock_component)
        assert isinstance(result, dict)
        assert result["ui_components"] == [mock_component]
