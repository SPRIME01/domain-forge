import json
from typing import Any, Dict, List, Union

import pytest
from lark import Lark, Token, Tree

from domainforge.core.transformer import DomainForgeTransformer


def tree_to_dict(node: Union[Tree, Token]) -> Dict[str, Any]:
    """Convert a Lark tree to a dictionary for easier inspection"""
    if isinstance(node, Tree):
        return {
            "type": "Tree",
            "data": node.data,
            "children": [tree_to_dict(child) for child in node.children],
        }
    else:  # Token
        return {"type": "Token", "token_type": node.type, "value": node.value}


def test_debug_parse_tree():
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

    parser = Lark(grammar, parser="lalr")

    dsl = """
    @Context {
        #Entity {
            name: String
        }
    }
    """
    tree = parser.parse(dsl)

    # Convert tree to a dictionary and display it as JSON
    tree_dict: Dict[str, Any] = tree_to_dict(tree)
    tree_json: str = json.dumps(tree_dict, indent=2)

    # Print the tree structure for debugging without failing
    print(f"\nParse Tree Structure:\n{tree_json}")

    # Instead of failing, let's assert that we got the expected structure
    # The expected structure is exactly what we already have in the JSON
    assert tree_dict["type"] == "Tree"
    assert tree_dict["data"] == "start"
    assert len(tree_dict["children"]) == 1

    # Check that the first child is a context definition
    context_def = tree_dict["children"][0]
    assert context_def["type"] == "Tree"
    assert context_def["data"] == "context_definition"

    # Verify the context has the expected name
    context_name = context_def["children"][0]
    assert context_name["type"] == "Token"
    assert context_name["token_type"] == "IDENTIFIER"
    assert context_name["value"] == "Context"


def test_debug_property_definition():
    """Debug test for property_definition transformer method."""
    transformer: DomainForgeTransformer = DomainForgeTransformer()

    # Create a simple property definition tree
    property_tree: Tree = Tree(
        "property_definition",
        [
            Token("IDENTIFIER", "name"),
            Tree(
                "type_definition",
                [Tree("simple_type", [Token("IDENTIFIER", "String")])],
            ),
        ],
    )

    # Directly transform the property definition
    result: Any = transformer.property_definition(property_tree.children)

    # Debug output
    print(f"\nDEBUG: Property transformation result = {result}")
    print(f"DEBUG: Result type = {type(result)}")

    # Test assertions
    assert result.name == "name"
    assert result.type == "String"
