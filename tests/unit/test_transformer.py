import pytest
from lark import Tree, Token
from src.core.transformer import DomainForgeTransformer
from src.core.models import (
    DomainModel,
    BoundedContext,
    Entity,
    ValueObject,
    Event,
    Service,
    Repository,
    Role,
    Module,
    Property,
    Method,
    ApiEndpoint,
    UiComponent,
    Relationship,
    Parameter,
)

@pytest.fixture
def transformer():
    return DomainForgeTransformer()

def test_transform_simple_entity(transformer):
    tree = Tree("start", [
        Tree("context_definition", [
            Token("IDENTIFIER", "Context"),
            Tree("entity_definition", [
                Token("IDENTIFIER", "Entity"),
                Tree("property_definition", [
                    Token("IDENTIFIER", "name"),
                    Token("IDENTIFIER", "String")
                ])
            ])
        ])
    ])
    model = transformer.transform(tree)
    assert isinstance(model, DomainModel)
    assert len(model.bounded_contexts) == 1
    context = model.bounded_contexts[0]
    assert context.name == "Context"
    assert len(context.entities) == 1
    entity = context.entities[0]
    assert entity.name == "Entity"
    assert len(entity.properties) == 1
    prop = entity.properties[0]
    assert prop.name == "name"
    assert prop.type == "String"

def test_transform_relationship(transformer):
    tree = Tree("start", [
        Tree("context_definition", [
            Token("IDENTIFIER", "Context"),
            Tree("entity_definition", [
                Token("IDENTIFIER", "Entity1"),
                Tree("property_definition", [
                    Token("IDENTIFIER", "name"),
                    Token("IDENTIFIER", "String")
                ])
            ]),
            Tree("entity_definition", [
                Token("IDENTIFIER", "Entity2"),
                Tree("property_definition", [
                    Token("IDENTIFIER", "description"),
                    Token("IDENTIFIER", "String")
                ])
            ]),
            Tree("relationship_definition", [
                Token("IDENTIFIER", "Entity1"),
                Token("RELATIONSHIP_SYMBOL", "->"),
                Token("IDENTIFIER", "Entity2")
            ])
        ])
    ])
    model = transformer.transform(tree)
    assert isinstance(model, DomainModel)
    assert len(model.bounded_contexts) == 1
    context = model.bounded_contexts[0]
    assert context.name == "Context"
    assert len(context.entities) == 2
    entity1 = context.entities[0]
    entity2 = context.entities[1]
    assert entity1.name == "Entity1"
    assert entity2.name == "Entity2"
    assert len(entity1.relationships) == 1
    relationship = entity1.relationships[0]
    assert relationship.source_entity == "Entity1"
    assert relationship.target_entity == "Entity2"
    assert relationship.relationship_type == "->"

def test_transform_service_with_method(transformer):
    tree = Tree("start", [
        Tree("context_definition", [
            Token("IDENTIFIER", "Context"),
            Tree("service_definition", [
                Token("IDENTIFIER", "Service"),
                Tree("method_definition", [
                    Token("IDENTIFIER", "doSomething"),
                    Tree("parameter_list", [
                        Tree("parameter", [
                            Token("IDENTIFIER", "param"),
                            Token("IDENTIFIER", "String")
                        ])
                    ]),
                    Token("IDENTIFIER", "Void")
                ])
            ])
        ])
    ])
    model = transformer.transform(tree)
    assert isinstance(model, DomainModel)
    assert len(model.bounded_contexts) == 1
    context = model.bounded_contexts[0]
    assert context.name == "Context"
    assert len(context.services) == 1
    service = context.services[0]
    assert service.name == "Service"
    assert len(service.methods) == 1
    method = service.methods[0]
    assert method.name == "doSomething"
    assert len(method.parameters) == 1
    param = method.parameters[0]
    assert param.name == "param"
    assert param.type == "String"
    assert method.return_type == "Void"
