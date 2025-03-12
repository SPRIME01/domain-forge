"""Unit tests for the domain elicitation session functionality."""

from domainforge.core.interpreter import DomainElicitationSession


class TestDomainElicitationSession:
    """Tests for the DomainElicitationSession class."""

    def test_initialization(self) -> None:
        """Test that a session initializes with correct defaults."""
        session = DomainElicitationSession("test-session-1")

        assert session.session_id == "test-session-1"
        assert session.domain_entities == {}
        assert session.relationships == []
        assert session.current_stage == "introduction"

    def test_add_entity(self) -> None:
        """Test adding entities to the session."""
        session = DomainElicitationSession("test-session-1")

        # Add a simple entity
        properties = ["name: String", "email: String", "active: Boolean"]
        session.add_entity("User", properties)

        assert "User" in session.domain_entities
        assert session.domain_entities["User"] == properties

        # Add another entity
        order_properties = ["id: UUID", "date: DateTime", "total: Decimal"]
        session.add_entity("Order", order_properties)

        assert len(session.domain_entities) == 2
        assert session.domain_entities["Order"] == order_properties

    def test_add_relationship(self) -> None:
        """Test adding relationships between entities."""
        session = DomainElicitationSession("test-session-1")

        # Add entities first
        session.add_entity("User", ["name: String"])
        session.add_entity("Order", ["total: Decimal"])

        # Add a relationship
        session.add_relationship("User", "Order", "=>")

        assert len(session.relationships) == 1
        relationship = session.relationships[0]
        assert relationship["source"] == "User"
        assert relationship["target"] == "Order"
        assert relationship["type"] == "=>"

        # Add another relationship
        session.add_relationship("Order", "User", "<->")

        assert len(session.relationships) == 2
        assert session.relationships[1]["source"] == "Order"
        assert session.relationships[1]["target"] == "User"
        assert session.relationships[1]["type"] == "<->"

    def test_get_domain_model(self) -> None:
        """Test retrieving the complete domain model."""
        session = DomainElicitationSession("test-session-1")

        # Add entities and relationships
        session.add_entity("User", ["name: String"])
        session.add_entity("Order", ["total: Decimal"])
        session.add_relationship("User", "Order", "=>")

        # Get the domain model
        model = session.get_domain_model()

        assert "entities" in model
        assert "relationships" in model
        assert len(model["entities"]) == 2
        assert len(model["relationships"]) == 1
        assert model["entities"]["User"] == ["name: String"]
        assert model["relationships"][0]["source"] == "User"
