"""UI component models for the domain-driven design framework."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union, Any
from enum import Enum


class ComponentType(Enum):
    """Enum for all supported UI component types."""

    PAGE = "Page"
    FORM = "Form"
    LIST = "List"
    TABLE = "Table"
    CARD = "Card"
    MODAL = "Modal"
    SIDEBAR = "Sidebar"
    NAVBAR = "Navbar"
    PANEL = "Panel"
    TABS = "Tabs"
    BUTTON = "Button"  
    TEXT = "Text"
    IMAGE = "Image"
    ICON = "Icon"
    CHECKBOX = "Checkbox"
    INPUT = "Input"
    SELECT = "Select"


class LayoutDirection(Enum):
    """Layout direction options for UI components."""

    ROW = "row"
    COLUMN = "column"
    ROW_REVERSE = "row-reverse"
    COLUMN_REVERSE = "column-reverse"


@dataclass
class LayoutProperties:
    """Layout properties for UI components including spacing and alignment."""

    direction: Optional[LayoutDirection] = None
    gap: Optional[Union[str, int]] = None
    align: Optional[str] = None
    justify: Optional[str] = None
    wrap: Optional[bool] = None
    padding: Optional[Union[str, int]] = None
    margin: Optional[Union[str, int]] = None
    width: Optional[Union[str, int]] = None
    height: Optional[Union[str, int]] = None


@dataclass
class NavigationRule:
    """Navigation rule for UI component interactions defining event handling."""

    event: str
    target: str
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UIComponent:
    """Represents a UI component."""

    component_type: ComponentType
    name: str
    properties: Dict[str, Any]
    layout: Optional[LayoutProperties] = None
    children: List["UIComponent"] = field(default_factory=list)
    navigation_rules: List[NavigationRule] = field(default_factory=list)

    @property
    def has_children(self) -> bool:
        """Check if the component has child components."""
        return len(self.children) > 0

    @property
    def has_navigation(self) -> bool:
        """Check if the component has navigation rules."""
        return len(self.navigation_rules) > 0

    def add_child(self, child: "UIComponent") -> None:
        """Add a child component."""
        self.children.append(child)

    def add_navigation_rule(
        self, event: str, target: str, params: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a navigation rule."""
        self.navigation_rules.append(NavigationRule(event, target, params or {}))

    def to_dict(self) -> Dict[str, Any]:
        """Convert the component to a dictionary representation."""
        result = {
            "type": self.component_type.value,
            "name": self.name,
            "properties": self.properties,
        }

        if self.layout:
            result["layout"] = {
                "direction": self.layout.direction.value if self.layout.direction else None,  # Convert enum to string safely
                "gap": self.layout.gap,
                "align": self.layout.align,
                "justify": self.layout.justify,
            }

        if self.has_children:
            result["children"] = [child.to_dict() for child in self.children]

        if self.has_navigation:
            result["navigation"] = [
                {
                    "event": rule.event,
                    "target": rule.target,
                    **({"params": rule.params} if rule.params else {}),
                }
                for rule in self.navigation_rules
            ]

        return result
