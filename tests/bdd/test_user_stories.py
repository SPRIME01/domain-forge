from pytest_bdd import scenarios, given, when, then
from src.core.interpreter import DomainForgeInterpreter
from src.core.models import DomainModel

scenarios('user_stories.feature')

@given('a DomainForge DSL file with the following content')
def dsl_file_content():
    return """
    @Context {
        #Entity {
            name: String
        }
    }
    """

@when('the DSL file is interpreted')
def interpret_dsl_file(dsl_file_content):
    interpreter = DomainForgeInterpreter()
    return interpreter.interpret(dsl_file_content)

@then('the resulting domain model should have a context named "Context"')
def check_context_name(interpret_dsl_file):
    model = interpret_dsl_file
    assert isinstance(model, DomainModel)
    assert len(model.bounded_contexts) == 1
    assert model.bounded_contexts[0].name == "Context"

@then('the context should have an entity named "Entity"')
def check_entity_name(interpret_dsl_file):
    model = interpret_dsl_file
    context = model.bounded_contexts[0]
    assert len(context.entities) == 1
    assert context.entities[0].name == "Entity"

@then('the entity should have a property named "name" of type "String"')
def check_entity_property(interpret_dsl_file):
    model = interpret_dsl_file
    entity = model.bounded_contexts[0].entities[0]
    assert len(entity.properties) == 1
    assert entity.properties[0].name == "name"
    assert entity.properties[0].type == "String"
