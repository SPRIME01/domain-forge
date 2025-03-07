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
            Tree("context_children", [
                Tree("entity_definition", [
                    Token("IDENTIFIER", "Entity"),
                    Tree("entity_children", [
                        Tree("property_definition", [
                            Token("IDENTIFIER", "name"),
                            Tree("type_definition", [
                                Tree("simple_type", [
                                    Token("IDENTIFIER", "String")
                                ])
                            ])
                        ])
                    ])
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
            Tree("context_children", [
                Tree("entity_definition", [
                    Token("IDENTIFIER", "Entity1"),
                    Tree("entity_children", [
                        Tree("property_definition", [
                            Token("IDENTIFIER", "name"),
                            Tree("type_definition", [
                                Tree("simple_type", [
                                    Token("IDENTIFIER", "String")
                                ])
                            ])
                        ])
                    ])
                ]),
                Tree("entity_definition", [
                    Token("IDENTIFIER", "Entity2"),
                    Tree("entity_children", [
                        Tree("property_definition", [
                            Token("IDENTIFIER", "description"),
                            Tree("type_definition", [
                                Tree("simple_type", [
                                    Token("IDENTIFIER", "String")
                                ])
                            ])
                        ])
                    ])
                ]),
                Tree("relationship_definition", [
                    Tree("source_entity", [
                        Token("IDENTIFIER", "Entity1")
                    ]),
                    Token("RELATIONSHIP_SYMBOL", "->"),
                    Tree("target_entity", [
                        Token("IDENTIFIER", "Entity2")
                    ])
                ])
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
            Tree("context_children", [
                Tree("service_definition", [
                    Token("IDENTIFIER", "Service"),
                    Tree("service_children", [
                        Tree("method_definition", [
                            Token("IDENTIFIER", "doSomething"),
                            Tree("parameter_list", [
                                Tree("parameter", [
                                    Token("IDENTIFIER", "param"),
                                    Tree("type_definition", [
                                        Tree("simple_type", [
                                            Token("IDENTIFIER", "String")
                                        ])
                                    ])
                                ])
                            ]),
                            Tree("return_type", [
                                Tree("type_definition", [
                                    Tree("simple_type", [
                                        Token("IDENTIFIER", "Void")
                                    ])
                                ])
                            ])
                        ])
                    ])
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

def test_transform_ui_component(transformer):
    tree = Tree("start", [
        Tree("context_definition", [
            Token("IDENTIFIER", "Context"),
            Tree("context_children", [
                Tree("entity_definition", [
                    Token("IDENTIFIER", "Entity"),
                    Tree("entity_children", [
                        Tree("ui_definition", [
                            Token("UI_COMPONENT", "Form"),
                            Tree("ui_desc", [
                                Tree("description", [
                                    Token("STRING", '"A form for the entity"')
                                ])
                            ])
                        ])
                    ])
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
    assert len(entity.uis) == 1
    ui = entity.uis[0]
    assert ui.component_type == "Form"
    assert ui.description == "A form for the entity"

def test_transform_api_definition(transformer):
    tree = Tree("start", [
        Tree("context_definition", [
            Token("IDENTIFIER", "Context"),
            Tree("context_children", [
                Tree("entity_definition", [
                    Token("IDENTIFIER", "Entity"),
                    Tree("entity_children", [
                        Tree("api_definition", [
                            Token("HTTP_METHOD", "GET"),
                            Token("STRING", '"/entities"'),
                            Tree("api_desc", [
                                Tree("description", [
                                    Token("STRING", '"Get all entities"')
                                ])
                            ])
                        ])
                    ])
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
    assert len(entity.apis) == 1
    api = entity.apis[0]
    assert api.http_method == "GET"
    assert api.path == "/entities"
    assert api.description == "Get all entities"
