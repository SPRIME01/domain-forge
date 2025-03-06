import pytest
from lark import Lark, Tree, Token

@pytest.fixture
def parser():
    grammar = """
    %import common.WS
    %import common.INT
    %import common.FLOAT
    %import common.WORD
    %import common.ESCAPED_STRING
    %ignore WS

    // --------------------- Terminals ---------------------

    // MODIFIERS: Modify relationships to indicate obligations or permissions.
    MODIFIER: "!"    // Must (Obligation)
            | "~"   // Should (Recommendation)
            | "?"   // May (Permission)

    // ENTITY SYMBOLS: Indicate the type of an entity.
    ENTITY_SYMBOL: "#"    // Entity (aggregate root)
                | "%"    // Value object
                | "^"    // Event
                | ">>"   // Service/Process
                | "&"    // Role/Actor
                | "@"    // Context/Bounded Context
                | "$"    // Repository
                | "*"    // Module/Package

    // RELATIONSHIP SYMBOLS: Represent various relationship types.
    RELATIONSHIP_SYMBOL: "=>"      // Dependency / Uses
                    | "<->"      // Bidirectional Association
                    | "--"       // Association
                    | "->"       // One-way Association
                    | "."        // Composition
                    | "::"       // Inheritance
                    | "/"        // Implementation
                    | "="        // Equivalence

    // API and UI annotations
    HTTP_METHOD: "GET" | "POST" | "PUT" | "DELETE" | "PATCH"
    UI_COMPONENT: "Form" | "Table" | "Card" | "Detail" | "List"
    VISIBILITY: "public" | "private" | "protected"

    // Symbols used for grouping expressions
    LPAREN: "("
    RPAREN: ")"
    LSQBRACKET: "["
    RSQBRACKET: "]"
    LCURLYBRACE: "{"
    RCURLYBRACE: "}"
    LANGELED: "<"
    RANGELED: ">"

    // Other separators
    ITEM_SEPARATOR: ","           // Separator in groups and collections
    COLON: ":"
    EQUALS: "="

    // Comments
    COMMENT: /\/\/[^\n]*/         // Single-line comments
        | /\/\*[\s\S]*?\*\//    // Multi-line comments
    %ignore COMMENT

    // IDENTIFIERS: Names for entities.
    IDENTIFIER: /[a-zA-Z_][a-zA-Z0-9_]*/

    // String literals
    STRING: ESCAPED_STRING

    // --------------------- Grammar Rules ---------------------

    // A complete domain model consists of one or more bounded contexts
    start: context_definition+

    // A bounded context defines a subsystem boundary
    context_definition: "@" IDENTIFIER LCURLYBRACE
                        (entity_definition
                        | value_object_definition
                        | event_definition
                        | service_definition
                        | repository_definition
                        | module_definition
                        | role_definition)*
                    RCURLYBRACE

    // Entity - aggregate root
    entity_definition: "#" IDENTIFIER (COLON IDENTIFIER)? LCURLYBRACE
                        (property_definition
                        | method_definition
                        | api_definition
                        | ui_definition)*
                    RCURLYBRACE

    // Value Object - immutable with no identity
    value_object_definition: "%" IDENTIFIER LCURLYBRACE
                            property_definition*
                        RCURLYBRACE

    // Event definition
    event_definition: "^" IDENTIFIER LCURLYBRACE
                    property_definition*
                    RCURLYBRACE

    // Service definition
    service_definition: ">>" IDENTIFIER LCURLYBRACE
                        (method_definition | api_definition)*
                    RCURLYBRACE

    // Repository definition
    repository_definition: "$" IDENTIFIER LCURLYBRACE
                        method_definition*
                    RCURLYBRACE

    // Module definition
    module_definition: "*" IDENTIFIER LCURLYBRACE
                        (entity_definition
                        | value_object_definition
                        | event_definition
                        | service_definition
                        | repository_definition)*
                    RCURLYBRACE

    // Role definition
    role_definition: "&" IDENTIFIER LCURLYBRACE
                    property_definition*
                    RCURLYBRACE

    // Property definition
    property_definition: IDENTIFIER COLON type_definition (EQUALS default_value)?
                        (LSQBRACKET constraint+ RSQBRACKET)?

    // Type definition including collections
    type_definition: IDENTIFIER              -> simple_type
                | IDENTIFIER LANGLED IDENTIFIER RANGLED  -> generic_type
                | "List" LANGLED type_definition RANGLED -> list_type
                | "Dict" LANGLED type_definition COLON type_definition RANGLED -> dict_type

    // Method definition
    method_definition: (VISIBILITY)? IDENTIFIER LPAREN parameter_list? RPAREN (COLON type_definition)?
                        (LCURLYBRACE description? RCURLYBRACE)?

    // Parameter list
    parameter_list: parameter (ITEM_SEPARATOR parameter)*

    // Parameter
    parameter: IDENTIFIER COLON type_definition (EQUALS default_value)?

    // Default value
    default_value: INT
                | FLOAT
                | STRING
                | IDENTIFIER
                | LSQBRACKET value_list? RSQBRACKET

    // Value list
    value_list: value (ITEM_SEPARATOR value)*

    // Value
    value: INT
        | FLOAT
        | STRING
        | IDENTIFIER
        | LSQBRACKET value_list? RSQBRACKET

    // Constraint
    constraint: "required"
            | "unique"
            | "min" COLON INT
            | "max" COLON INT
            | "pattern" COLON STRING
            | "foreign_key" COLON IDENTIFIER

    // Relationship definition
    relationship_definition: source_entity RELATIONSHIP_SYMBOL target_entity (LCURLYBRACE description RCURLYBRACE)?

    // Source and target entities
    source_entity: IDENTIFIER
    target_entity: IDENTIFIER

    // Description
    description: STRING

    // API definition
    api_definition: "api" COLON HTTP_METHOD STRING (LPAREN parameter_list? RPAREN)?
                (COLON type_definition)? (LCURLYBRACE description? RCURLYBRACE)?

    // UI definition
    ui_definition: "ui" COLON UI_COMPONENT (LPAREN parameter_list? RPAREN)?
                (LCURLYBRACE description? RCURLYBRACE)?
    """
    return Lark(grammar, start='start', parser='lalr')

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
