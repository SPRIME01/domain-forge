import pytest
from lark import Tree, Token
from src.core.parser import DomainForgeParser

@pytest.fixture
def parser():
    return DomainForgeParser()

def test_parse_simple_entity(parser):
    dsl = """
    @Context {
        #Entity {
            name: String
        }
    }
    """
    tree = parser.parse(dsl)
    assert isinstance(tree, Tree)
    assert tree.data == "start"
    assert len(tree.children) == 1
    context = tree.children[0]
    assert context.data == "context_definition"
    assert len(context.children) == 2
    assert context.children[0] == Token("IDENTIFIER", "Context")
    entity = context.children[1].children[0]
    assert entity.data == "entity_definition"
    assert entity.children[0] == Token("IDENTIFIER", "Entity")
    assert entity.children[1].data == "property_definition"
    assert entity.children[1].children[0] == Token("IDENTIFIER", "name")
    assert entity.children[1].children[1] == Token("IDENTIFIER", "String")

def test_parse_relationship(parser):
    dsl = """
    @Context {
        #Entity1 {
            name: String
        }
        #Entity2 {
            description: String
        }
        Entity1 -> Entity2
    }
    """
    tree = parser.parse(dsl)
    assert isinstance(tree, Tree)
    assert tree.data == "start"
    assert len(tree.children) == 1
    context = tree.children[0]
    assert context.data == "context_definition"
    assert len(context.children) == 4
    assert context.children[0] == Token("IDENTIFIER", "Context")
    entity1 = context.children[1].children[0]
    assert entity1.data == "entity_definition"
    assert entity1.children[0] == Token("IDENTIFIER", "Entity1")
    assert entity1.children[1].data == "property_definition"
    assert entity1.children[1].children[0] == Token("IDENTIFIER", "name")
    assert entity1.children[1].children[1] == Token("IDENTIFIER", "String")
    entity2 = context.children[2].children[0]
    assert entity2.data == "entity_definition"
    assert entity2.children[0] == Token("IDENTIFIER", "Entity2")
    assert entity2.children[1].data == "property_definition"
    assert entity2.children[1].children[0] == Token("IDENTIFIER", "description")
    assert entity2.children[1].children[1] == Token("IDENTIFIER", "String")
    relationship = context.children[3]
    assert relationship.data == "relationship_definition"
    assert relationship.children[0] == Token("IDENTIFIER", "Entity1")
    assert relationship.children[1] == Token("RELATIONSHIP_SYMBOL", "->")
    assert relationship.children[2] == Token("IDENTIFIER", "Entity2")

def test_parse_service_with_method(parser):
    dsl = """
    @Context {
        >>Service {
            doSomething(param: String): Void
        }
    }
    """
    tree = parser.parse(dsl)
    assert isinstance(tree, Tree)
    assert tree.data == "start"
    assert len(tree.children) == 1
    context = tree.children[0]
    assert context.data == "context_definition"
    assert len(context.children) == 2
    assert context.children[0] == Token("IDENTIFIER", "Context")
    service = context.children[1].children[0]
    assert service.data == "service_definition"
    assert service.children[0] == Token("IDENTIFIER", "Service")
    method = service.children[1]
    assert method.data == "method_definition"
    assert method.children[0] == Token("IDENTIFIER", "doSomething")
    assert method.children[1].data == "parameter_list"
    assert method.children[1].children[0].data == "parameter"
    assert method.children[1].children[0].children[0] == Token("IDENTIFIER", "param")
    assert method.children[1].children[0].children[1] == Token("IDENTIFIER", "String")
    assert method.children[2] == Token("IDENTIFIER", "Void")
