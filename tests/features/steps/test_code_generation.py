"""
Steps for code generation feature tests.

This module contains step definitions for the code generation feature tests.
"""

import os
import ast
from pytest_bdd import given, when, then
from domainforge.core.code_generation import CodeGenerator


@given("the code generation system is initialized")
def initialize_code_generation_system(context) -> None:
    """Initialize the code generation system."""
    context.code_gen_context = CodeGenerator()
    context.code_gen_context.initialize()


@given("the output directory is empty")
def empty_output_directory(context) -> None:
    """Ensure the output directory is empty."""
    context.code_gen_context.empty_output_directory()


@when('I request generation of a domain entity "{entity_name}"')
def request_generation_of_domain_entity(context, entity_name: str) -> None:
    """Request generation of a domain entity."""
    context.code_gen_context.entity_name = entity_name


@when("I specify the following properties:")
def specify_properties(context) -> None:
    """Specify properties for the domain entity."""
    properties = []
    for row in context.table:
        properties.append(
            {
                "name": row["name"],
                "type": row["type"],
                "required": row["required"] == "yes",
            }
        )
    context.code_gen_context.properties = properties


@then('a file "{file_name}" should be created')
def verify_file_created(context, file_name: str) -> None:
    """Verify that a file is created."""
    output_dir = context.code_gen_context.output_dir
    assert os.path.exists(os.path.join(output_dir, file_name)), (
        f"File {file_name} not found in {output_dir}"
    )


@then('the file should contain a class "{class_name}"')
def verify_class_in_file(context, class_name: str) -> None:
    """Verify that the file contains a class."""
    output_dir = context.code_gen_context.output_dir
    entity_file = None
    for f_name in os.listdir(output_dir):
        if (
            f_name.endswith(".py")
            and class_name.lower() in f_name.lower()
            and not f_name.startswith("test_")
        ):
            entity_file = f_name
            break

    assert entity_file is not None, f"Could not find file for class {class_name}"

    file_path = os.path.join(output_dir, entity_file)
    with open(file_path, "r") as f:
        content = f.read()

    tree = ast.parse(content)
    target_class = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            target_class = node
            break
    assert target_class is not None, f"Class {class_name} not found in {entity_file}"


@then("the class should have all specified properties")
def verify_properties(context) -> None:
    """Verify that the class has all specified properties."""
    code_gen_context = context.code_gen_context
    entity_file = None
    for f_name in os.listdir(code_gen_context.output_dir):
        if (
            f_name.endswith(".py")
            and code_gen_context.entity_name.lower() in f_name.lower()
            and not f_name.startswith("test_")
        ):
            entity_file = f_name
            break

    assert entity_file is not None, (
        f"Could not find file for entity {code_gen_context.entity_name}"
    )

    file_path = os.path.join(code_gen_context.output_dir, entity_file)
    with open(file_path, "r") as f:
        content = f.read()

    tree = ast.parse(content)
    target_class = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == code_gen_context.entity_name:
            target_class = node
            break
    assert target_class is not None, (
        f"Class {code_gen_context.entity_name} not found in {entity_file}"
    )

    class_fields = set()
    for node in target_class.body:
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            class_fields.add(node.target.id)

    for prop in code_gen_context.properties:
        prop_name = prop["name"]
        assert prop_name in class_fields, (
            f"Property '{prop_name}' not found in class {code_gen_context.entity_name}"
        )
