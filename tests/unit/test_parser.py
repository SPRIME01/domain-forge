import pytest
from lark import Lark, Tree, Token

@pytest.fixture
def parser():
    # Define the grammar using Lark's EBNF syntax - with explicit tree structure
    grammar = r"""
    start: context_definition+

    context_definition: "@" IDENTIFIER "{" context_children "}"
    context_children: (entity_definition | value_object_definition | event_definition | service_definition | repository_definition | module_definition | role_definition | relationship_definition)*

    entity_definition: "#" IDENTIFIER entity_inheritance? "{" entity_children "}"
    entity_inheritance: ":" IDENTIFIER
    entity_children: (property_definition | method_definition | api_definition | ui_definition)*

    value_object_definition: "%" IDENTIFIER "{" property_definition* "}"
    event_definition: "^" IDENTIFIER "{" property_definition* "}"
    service_definition: ">>" IDENTIFIER "{" service_children "}"
    service_children: (method_definition | api_definition)*
    repository_definition: "$" IDENTIFIER "{" method_definition* "}"
    module_definition: "*" IDENTIFIER "{" module_children "}"
    module_children: (entity_definition | value_object_definition | event_definition | service_definition | repository_definition)*
    role_definition: "&" IDENTIFIER "{" property_definition* "}"

    property_definition: IDENTIFIER ":" type_definition property_default? property_constraint?
    property_default: "=" default_value
    property_constraint: "[" constraint+ "]"

    type_definition: simple_type | generic_type | list_type | dict_type
    simple_type: IDENTIFIER
    generic_type: IDENTIFIER "<" IDENTIFIER ">"
    list_type: "List" "<" type_definition ">"
    dict_type: "Dict" "<" type_definition ":" type_definition ">"

    method_definition: visibility? IDENTIFIER "(" parameter_list? ")" return_type? method_body?
    visibility: VISIBILITY
    return_type: ":" type_definition
    method_body: "{" description? "}"

    parameter_list: parameter ("," parameter)*
    parameter: IDENTIFIER ":" type_definition parameter_default?
    parameter_default: "=" default_value

    default_value: INT | FLOAT | STRING | IDENTIFIER | list_value
    list_value: "[" value_list? "]"
    value_list: value ("," value)*
    value: INT | FLOAT | STRING | IDENTIFIER | list_value

    constraint: "required" | "unique" | min_constraint | max_constraint | pattern_constraint | fk_constraint
    min_constraint: "min" ":" INT
    max_constraint: "max" ":" INT
    pattern_constraint: "pattern" ":" STRING
    fk_constraint: "foreign_key" ":" IDENTIFIER

    relationship_definition: source_entity RELATIONSHIP_SYMBOL target_entity relationship_desc?
    relationship_desc: "{" description? "}"
    source_entity: IDENTIFIER
    target_entity: IDENTIFIER

    description: STRING

    api_definition: "api" ":" HTTP_METHOD STRING api_params? api_return? api_desc?
    api_params: "(" parameter_list? ")"
    api_return: ":" type_definition
    api_desc: "{" description? "}"

    ui_definition: "ui" ":" UI_COMPONENT ui_params? ui_desc?
    ui_params: "(" parameter_list? ")"
    ui_desc: "{" description? "}"

    // Terminals
    IDENTIFIER: /[a-zA-Z_][a-zA-Z0-9_]*/
    RELATIONSHIP_SYMBOL: "=>" | "<->" | "--" | "->" | "." | "::" | "/" | "="
    HTTP_METHOD: "GET" | "POST" | "PUT" | "DELETE" | "PATCH"
    UI_COMPONENT: "Form" | "Table" | "Card" | "Detail" | "List"
    VISIBILITY: "public" | "private" | "protected"

    STRING: /"[^"]*"/

    %import common.INT
    %import common.FLOAT
    %import common.WS

    COMMENT: /\/\/[^\n]*/ | /\/\*[\s\S]*?\*\//
    %ignore COMMENT
    %ignore WS
    """

    return Lark(grammar, parser='lalr')

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
    assert context.children[0] == Token("IDENTIFIER", "Context")

    context_children = context.children[1]
    assert context_children.data == "context_children"

    entity = context_children.children[0]
    assert entity.data == "entity_definition"
    assert entity.children[0] == Token("IDENTIFIER", "Entity")

    entity_children = entity.children[1]
    assert entity_children.data == "entity_children"

    prop = entity_children.children[0]
    assert prop.data == "property_definition"
    assert prop.children[0] == Token("IDENTIFIER", "name")

    prop_type = prop.children[1]
    assert prop_type.data == "type_definition"

    simple_type = prop_type.children[0]
    assert simple_type.data == "simple_type"
    assert simple_type.children[0] == Token("IDENTIFIER", "String")

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

    context = tree.children[0]
    assert context.data == "context_definition"
    assert context.children[0] == Token("IDENTIFIER", "Context")

    context_children = context.children[1]
    assert context_children.data == "context_children"

    entity1 = context_children.children[0]
    assert entity1.data == "entity_definition"
    assert entity1.children[0] == Token("IDENTIFIER", "Entity1")

    entity2 = context_children.children[1]
    assert entity2.data == "entity_definition"
    assert entity2.children[0] == Token("IDENTIFIER", "Entity2")

    relationship = context_children.children[2]
    assert relationship.data == "relationship_definition"

    source = relationship.children[0]
    assert source.data == "source_entity"
    assert source.children[0] == Token("IDENTIFIER", "Entity1")

    rel_symbol = relationship.children[1]
    assert rel_symbol == Token("RELATIONSHIP_SYMBOL", "->")

    target = relationship.children[2]
    assert target.data == "target_entity"
    assert target.children[0] == Token("IDENTIFIER", "Entity2")

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

    context = tree.children[0]
    assert context.data == "context_definition"
    assert context.children[0] == Token("IDENTIFIER", "Context")

    context_children = context.children[1]
    assert context_children.data == "context_children"

    service = context_children.children[0]
    assert service.data == "service_definition"
    assert service.children[0] == Token("IDENTIFIER", "Service")

    service_children = service.children[1]
    assert service_children.data == "service_children"

    method = service_children.children[0]
    assert method.data == "method_definition"
    assert method.children[0] == Token("IDENTIFIER", "doSomething")

    param_list = method.children[1]
    assert param_list.data == "parameter_list"

    param = param_list.children[0]
    assert param.data == "parameter"
    assert param.children[0] == Token("IDENTIFIER", "param")

    param_type = param.children[1]
    assert param_type.data == "type_definition"

    simple_type = param_type.children[0]
    assert simple_type.data == "simple_type"
    assert simple_type.children[0] == Token("IDENTIFIER", "String")

    return_type = method.children[2]
    assert return_type.data == "return_type"

    return_type_def = return_type.children[0]
    assert return_type_def.data == "type_definition"

    return_simple_type = return_type_def.children[0]
    assert return_simple_type.data == "simple_type"
    assert return_simple_type.children[0] == Token("IDENTIFIER", "Void")

def test_parse_ui_component(parser):
    dsl = """
    @Context {
        #Entity {
            ui: Form {
                "A form for the entity"
            }
        }
    }
    """
    tree = parser.parse(dsl)
    assert isinstance(tree, Tree)
    assert tree.data == "start"

    context = tree.children[0]
    assert context.data == "context_definition"
    assert context.children[0] == Token("IDENTIFIER", "Context")

    context_children = context.children[1]
    assert context_children.data == "context_children"

    entity = context_children.children[0]
    assert entity.data == "entity_definition"
    assert entity.children[0] == Token("IDENTIFIER", "Entity")

    entity_children = entity.children[1]
    assert entity_children.data == "entity_children"

    ui = entity_children.children[0]
    assert ui.data == "ui_definition"
    assert ui.children[0] == Token("UI_COMPONENT", "Form")

    ui_desc = ui.children[1]
    assert ui_desc.data == "ui_desc"

    description = ui_desc.children[0]
    assert description.data == "description"
    assert description.children[0] == Token("STRING", '"A form for the entity"')

def test_parse_api_definition(parser):
    dsl = """
    @Context {
        #Entity {
            api: GET "/entities" {
                "Get all entities"
            }
        }
    }
    """
    tree = parser.parse(dsl)
    assert isinstance(tree, Tree)
    assert tree.data == "start"

    context = tree.children[0]
    assert context.data == "context_definition"
    assert context.children[0] == Token("IDENTIFIER", "Context")

    context_children = context.children[1]
    assert context_children.data == "context_children"

    entity = context_children.children[0]
    assert entity.data == "entity_definition"
    assert entity.children[0] == Token("IDENTIFIER", "Entity")

    entity_children = entity.children[1]
    assert entity_children.data == "entity_children"

    api = entity_children.children[0]
    assert api.data == "api_definition"
    assert api.children[0] == Token("HTTP_METHOD", "GET")
    assert api.children[1] == Token("STRING", '"/entities"')

    api_desc = api.children[2]
    assert api_desc.data == "api_desc"

    description = api_desc.children[0]
    assert description.data == "description"
    assert description.children[0] == Token("STRING", '"Get all entities"')
