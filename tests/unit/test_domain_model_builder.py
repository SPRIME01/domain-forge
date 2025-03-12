"""Unit tests for the domain model builder functionality."""

from domainforge.core.interpreter import DomainModelBuilder


class TestDomainModelBuilder:
    """Tests for the DomainModelBuilder class."""

    def test_initialization(self) -> None:
        """Test that a model builder initializes with empty collections."""
        builder = DomainModelBuilder()

        assert builder.entities == {}
        assert builder.relationships == []

    def test_add_entity(self) -> None:
        """Test adding entities to the model."""
        builder = DomainModelBuilder()

        # Add a simple entity
        properties = ["name: String", "email: String", "active: Boolean"]
        builder.add_entity("User", properties)

        assert "User" in builder.entities
        assert builder.entities["User"] == properties

        # Add another entity
        order_properties = ["id: UUID", "date: DateTime", "total: Decimal"]
        builder.add_entity("Order", order_properties)

        assert len(builder.entities) == 2
        assert builder.entities["Order"] == order_properties

    def test_add_relationship(self) -> None:
        """Test adding relationships between entities."""
        builder = DomainModelBuilder()

        # Add entities first
        builder.add_entity("User", ["name: String"])
        builder.add_entity("Order", ["total: Decimal"])

        # Add a relationship
        builder.add_relationship("User", "Order", "=>")

        assert len(builder.relationships) == 1
        relationship = builder.relationships[0]
        assert relationship["source"] == "User"
        assert relationship["target"] == "Order"
        assert relationship["type"] == "=>"

        # Add another relationship with different type
        builder.add_relationship("Order", "Product", "--")

        assert len(builder.relationships) == 2
        assert builder.relationships[1]["source"] == "Order"
        assert builder.relationships[1]["target"] == "Product"
        assert builder.relationships[1]["type"] == "--"

    def test_get_domain_model(self) -> None:
        """Test retrieving the complete domain model."""
        builder = DomainModelBuilder()

        # Add entities and relationships
        builder.add_entity("User", ["name: String"])
        builder.add_entity("Order", ["total: Decimal"])
        builder.add_relationship("User", "Order", "=>")

        # Get the domain model
        model = builder.get_domain_model()

        assert "entities" in model
        assert "relationships" in model
        assert len(model["entities"]) == 2
        assert len(model["relationships"]) == 1
        assert model["entities"]["User"] == ["name: String"]
        assert model["relationships"][0]["type"] == "=>"

    def test_model_serialization(self) -> None:
        """Test the model can be properly serialized to JSON."""
        import json

        builder = DomainModelBuilder()
        builder.add_entity("User", ["name: String", "email: String"])
        builder.add_entity("Order", ["id: UUID", "total: Decimal"])
        builder.add_relationship("User", "Order", "=>")

        # Get model and serialize to JSON
        model = builder.get_domain_model()
        serialized = json.dumps(model)
        deserialized = json.loads(serialized)

        # Verify serialization/deserialization works correctly
        assert deserialized["entities"]["User"] == ["name: String", "email: String"]
        assert deserialized["relationships"][0]["source"] == "User"
        assert deserialized["relationships"][0]["target"] == "Order"
