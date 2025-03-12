"""Unit tests for the domain-specific language generator."""

from typing import Dict, Any

from domainforge.core.interpreter import DomainForgeDSLGenerator


class TestDomainForgeDSLGenerator:
    """Tests for the DomainForgeDSLGenerator class."""

    def test_empty_model_generation(self) -> None:
        """Test generating DSL from an empty domain model."""
        generator = DomainForgeDSLGenerator()
        empty_model: Dict[str, Any] = {}

        result = generator.generate_dsl(empty_model)

        assert result == ""

    def test_single_context_generation(self) -> None:
        """Test generating DSL for a single context with one entity."""
        generator = DomainForgeDSLGenerator()

        # Simple model with one context and one entity
        model = {
            "MainContext": {
                "entities": {"User": ["name: String", "email: String"]},
                "relationships": [],
            }
        }

        result = generator.generate_dsl(model)

        # Verify the DSL structure
        assert "@MainContext {" in result
        assert "#User {" in result
        assert "name: String" in result
        assert "email: String" in result
        assert "}" in result  # Closing brackets

    def test_relationships_generation(self) -> None:
        """Test generating DSL with relationships between entities."""
        generator = DomainForgeDSLGenerator()

        # Model with relationships
        model = {
            "ECommerce": {
                "entities": {"User": ["name: String"], "Order": ["total: Decimal"]},
                "relationships": [{"source": "User", "target": "Order", "type": "=>"}],
            }
        }

        result = generator.generate_dsl(model)

        # Verify relationships are included
        assert "User => Order" in result

    def test_multi_context_generation(self) -> None:
        """Test generating DSL with multiple contexts."""
        generator = DomainForgeDSLGenerator()

        # Model with multiple contexts
        model = {
            "UserManagement": {
                "entities": {"User": ["name: String", "role: String"]},
                "relationships": [],
            },
            "OrderProcessing": {
                "entities": {"Order": ["id: UUID", "status: String"]},
                "relationships": [],
            },
        }

        result = generator.generate_dsl(model)

        # Verify both contexts are included
        assert "@UserManagement {" in result
        assert "@OrderProcessing {" in result
        assert "#User {" in result
        assert "#Order {" in result

    def test_complex_model_generation(self) -> None:
        """Test generating DSL from a complex domain model."""
        generator = DomainForgeDSLGenerator()

        # Complex model with multiple contexts, entities, and relationships
        model = {
            "Sales": {
                "entities": {
                    "Customer": ["name: String", "email: String"],
                    "Order": ["id: UUID", "date: DateTime", "status: String"],
                    "Product": ["name: String", "price: Decimal", "sku: String"],
                },
                "relationships": [
                    {"source": "Customer", "target": "Order", "type": "=>"},
                    {"source": "Order", "target": "Product", "type": "<->"},
                ],
            },
            "Inventory": {
                "entities": {
                    "Stock": ["quantity: Integer", "location: String"],
                    "Warehouse": ["name: String", "address: String"],
                },
                "relationships": [
                    {"source": "Stock", "target": "Warehouse", "type": "->"}
                ],
            },
        }

        result = generator.generate_dsl(model)

        # Verify structure and content
        assert "@Sales {" in result
        assert "@Inventory {" in result
        assert "#Customer {" in result
        assert "#Order {" in result
        assert "#Product {" in result
        assert "#Stock {" in result
        assert "#Warehouse {" in result
        assert "Customer => Order" in result
        assert "Order <-> Product" in result
        assert "Stock -> Warehouse" in result
