from pathlib import Path
import pytest
from typing import Any

from domainforge.core.interpreter import DomainForgeInterpreter
from domainforge.core.models import DomainModel


@pytest.fixture
def interpreter() -> DomainForgeInterpreter:
    return DomainForgeInterpreter()


def test_interpret_simple_entity(interpreter: DomainForgeInterpreter) -> None:
    dsl: str = """
    @Context {
        #Entity {
            name: String
        }
    }
    """
    model: DomainModel = interpreter.interpret(dsl)
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


def test_interpret_relationship(interpreter: DomainForgeInterpreter) -> None:
    dsl: str = """
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
    model: DomainModel = interpreter.interpret(dsl)
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


def test_interpret_service_with_method(interpreter: DomainForgeInterpreter) -> None:
    dsl: str = """
    @Context {
        >>Service {
            doSomething(param: String): Void
        }
    }
    """
    model: DomainModel = interpreter.interpret(dsl)
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


def test_interpret_file(interpreter: DomainForgeInterpreter, tmp_path: Path) -> None:
    dsl: str = """
    @Context {
        #Entity {
            name: String
        }
    }
    """
    file_path: Path = tmp_path / "test.domainforge"
    file_path.write_text(dsl)
    model: DomainModel = interpreter.interpret_file(file_path)
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


def test_export_model(interpreter: DomainForgeInterpreter, tmp_path: Path) -> None:
    dsl: str = """
    @Context {
        #Entity {
            name: String
        }
    }
    """
    model: DomainModel = interpreter.interpret(dsl)
    output_path: Path = tmp_path / "domain_model.json"
    interpreter.export_model(model, output_path)
    assert output_path.exists()
    exported_data: str = output_path.read_text()
    assert '"name": "Context"' in exported_data
    assert '"name": "Entity"' in exported_data
    assert '"name": "name"' in exported_data
    assert '"type": "String"' in exported_data
