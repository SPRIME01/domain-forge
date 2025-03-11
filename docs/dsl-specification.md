# DomainForge DSL Specification

This document provides a detailed specification for the DomainForge Domain-Specific Language (DSL) used to generate full-stack applications with a Python backend and TypeScript frontend based on clean architecture and Domain-Driven Design (DDD) principles.

## Overview

DomainForge DSL allows you to define your domain model in a clear, structured way. The DSL supports various DDD concepts such as entities, value objects, aggregates, services, repositories, and more. This document outlines the grammar, parser, transformer, and interpreter for the DSL, along with examples and usage instructions.

## Grammar

The DomainForge DSL grammar is defined using Lark. The grammar supports the following components:

* Bounded Contexts: Represented with `@ContextName { ... }`
* Entities: Represented with `#EntityName { ... }`
* Value Objects: Represented with `%ValueObjectName { ... }`
* Events: Represented with `^EventName { ... }`
* Services: Represented with `>>ServiceName { ... }`
* Repositories: Represented with `$RepositoryName { ... }`
* Modules: Represented with `*ModuleName { ... }`
* Roles: Represented with `&RoleName { ... }`
* Relationships: Connected using various symbols like `=>`, `<->`, etc.
* Properties: Defined as `name: Type [constraints]`
* Methods: Defined as `methodName(parameters) { ... }`
* API Endpoints: Defined as `api: METHOD "/path"`
* UI Components: Defined as `ui: ComponentType`

### Grammar (domainforge.lark)

```lark
%import common.WS
%import common.INT
%import common.FLOAT
%import common.WORD
%import common.ESCAPED_STRING
%ignore WS

MODIFIER: "!" | "~" | "?"
ENTITY_SYMBOL: "#" | "%" | "^" | ">>" | "&" | "@" | "$" | "*"
RELATIONSHIP_SYMBOL: "=>" | "<->" | "--" | "->" | "." | "::" | "/"
HTTP_METHOD: "GET" | "POST" | "PUT" | "DELETE" | "PATCH"
UI_COMPONENT: "Form" | "Table" | "Card" | "Detail" | "List"
VISIBILITY: "public" | "private" | "protected"
LPAREN: "("
RPAREN: ")"
LSQBRACKET: "["
RSQBRACKET: "]"
LCURLYBRACE: "{"
RCURLYBRACE: "}"
LANGLED: "<"
RANGLED: ">"
ITEM_SEPARATOR: ","
COLON: ":"
COMMENT: /\/\/[^\n]*/ | /\/\*[\s\S]*?\*\//
%ignore COMMENT
IDENTIFIER: /[a-zA-Z_][a-zA-Z0-9_]*/
STRING: ESCAPED_STRING

start: context_definition+
context_definition: "@" IDENTIFIER LCURLYBRACE (entity_definition | value_object_definition | event_definition | service_definition | repository_definition | module_definition | role_definition)* RCURLYBRACE
entity_definition: "#" IDENTIFIER (COLON IDENTIFIER)? LCURLYBRACE (property_definition | method_definition | api_definition | ui_definition)* RCURLYBRACE
value_object_definition: "%" IDENTIFIER LCURLYBRACE property_definition* RCURLYBRACE
event_definition: "^" IDENTIFIER LCURLYBRACE property_definition* RCURLYBRACE
service_definition: ">>" IDENTIFIER LCURLYBRACE (method_definition | api_definition)* RCURLYBRACE
repository_definition: "$" IDENTIFIER LCURLYBRACE method_definition* RCURLYBRACE
module_definition: "*" IDENTIFIER LCURLYBRACE (entity_definition | value_object_definition | event_definition | service_definition | repository_definition)* RCURLYBRACE
role_definition: "&" IDENTIFIER LCURLYBRACE property_definition* RCURLYBRACE
property_definition: IDENTIFIER COLON type_definition (EQUALS default_value)? (LSQBRACKET constraint RSQBRACKET)?
type_definition: IDENTIFIER | IDENTIFIER LANGLED IDENTIFIER RANGLED | "List" LANGLED type_definition RANGLED | "Dict" LANGLED type_definition COLON type_definition RANGLED
method_definition: (VISIBILITY)? IDENTIFIER LPAREN parameter_list? RPAREN (COLON type_definition)? (LCURLYBRACE description? RCURLYBRACE)?
parameter_list: parameter (ITEM_SEPARATOR parameter)*
parameter: IDENTIFIER COLON type_definition (EQUALS default_value)?
default_value: INT | FLOAT | STRING | IDENTIFIER | LSQBRACKET value_list? RSQBRACKET
value_list: value (ITEM_SEPARATOR value)*
value: INT | FLOAT | STRING | IDENTIFIER | LSQBRACKET value_list? RSQBRACKET
constraint: "required" | "unique" | "min" COLON INT | "max" COLON INT | "pattern" COLON STRING | "foreign_key" COLON IDENTIFIER
relationship_definition: source_entity RELATIONSHIP_SYMBOL target_entity (LCURLYBRACE description RCURLYBRACE)?
source_entity: IDENTIFIER
target_entity: IDENTIFIER
description: STRING
api_definition: "api" COLON HTTP_METHOD STRING (LPAREN parameter_list? RPAREN)? (COLON type_definition)? (LCURLYBRACE description? RCURLYBRACE)?
ui_definition: "ui" COLON UI_COMPONENT (LPAREN parameter_list? RPAREN)? (LCURLYBRACE description? RCURLYBRACE)?
```

## Parser

The parser is implemented using Lark and reads the DSL file to generate a parse tree.

### Parser Implementation (parser.py)

```python
import os
from lark import Lark
from pathlib import Path

class DomainForgeParser:
    def __init__(self):
        current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        grammar_file = current_dir / "domainforge.lark"
        with open(grammar_file, 'r') as f:
            grammar = f.read()
        self.parser = Lark(grammar, start='start', parser='lalr')

    def parse(self, text):
        return self.parser.parse(text)

    def parse_file(self, file_path):
        with open(file_path, 'r') as f:
            text = f.read()
        return self.parse(text)
```

## Transformer

The transformer converts the parse tree into Pydantic models representing the domain model.

### Transformer Implementation (transformer.py)

```python
from lark import Transformer, v_args
from models import (
    BoundedContext, Entity, ValueObject, Event, Service,
    Repository, Module, Role, Property, Method, Parameter,
    ApiEndpoint, UiComponent, Relationship
)

@v_args(inline=True)
class DomainForgeTransformer(Transformer):
    def start(self, *contexts):
        return list(contexts)

    def context_definition(self, name, *elements):
        context_name = str(name)
        entities = [e for e in elements if isinstance(e, Entity)]
        value_objects = [e for e in elements if isinstance(e, ValueObject)]
        events = [e for e in elements if isinstance(e, Event)]
        services = [e for e in elements if isinstance(e, Service)]
        repositories = [e for e in elements if isinstance(e, Repository)]
        modules = [e for e in elements if isinstance(e, Module)]
        roles = [e for e in elements if isinstance(e, Role)]
        return BoundedContext(
            name=context_name,
            entities=entities,
            value_objects=value_objects,
            events=events,
            services=services,
            repositories=repositories,
            modules=modules,
            roles=roles
        )

    def entity_definition(self, name, *elements):
        entity_name = str(name)
        parent = None
        if len(elements) > 0 and isinstance(elements[0], str) and elements[0].startswith(':'):
            parent = elements[0][1:]
            elements = elements[1:]
        properties = [e for e in elements if isinstance(e, Property)]
        methods = [e for e in elements if isinstance(e, Method)]
        apis = [e for e in elements if isinstance(e, ApiEndpoint)]
        uis = [e for e in elements if isinstance(e, UiComponent)]
        return Entity(
            name=entity_name,
            parent=parent,
            properties=properties,
            methods=methods,
            apis=apis,
            uis=uis
        )

    def value_object_definition(self, name, *properties):
        vo_name = str(name)
        return ValueObject(
            name=vo_name,
            properties=properties
        )

    def event_definition(self, name, *properties):
        event_name = str(name)
        return Event(
            name=event_name,
            properties=properties
        )

    def service_definition(self, name, *elements):
        service_name = str(name)
        methods = [e for e in elements if isinstance(e, Method)]
        apis = [e for e in elements if isinstance(e, ApiEndpoint)]
        return Service(
            name=service_name,
            methods=methods,
            apis=apis
        )

    def repository_definition(self, name, *methods):
        repo_name = str(name)
        return Repository(
            name=repo_name,
            methods=methods
        )

    def module_definition(self, name, *elements):
        module_name = str(name)
        entities = [e for e in elements if isinstance(e, Entity)]
        value_objects = [e for e in elements if isinstance(e, ValueObject)]
        events = [e for e in elements if isinstance(e, Event)]
        services = [e for e in elements if isinstance(e, Service)]
        repositories = [e for e in elements if isinstance(e, Repository)]
        return Module(
            name=module_name,
            entities=entities,
            value_objects=value_objects,
            events=events,
            services=services,
            repositories=repositories
        )

    def role_definition(self, name, *properties):
        role_name = str(name)
        return Role(
            name=role_name,
            properties=properties
        )

    def property_definition(self, name, type_def, *rest):
        prop_name = str(name)
        default_value = None
        constraints = []
        for item in rest:
            if isinstance(item, tuple) and item[0] == 'default':
                default_value = item[1]
            elif isinstance(item, str) and item.startswith('['):
                constraints.append(item[1:-1])
        return Property(
            name=prop_name,
            type=type_def,
            default_value=default_value,
            constraints=constraints
        )

    def simple_type(self, type_name):
        return str(type_name)

    def generic_type(self, container, content):
        return f"{container}<{content}>"

    def list_type(self, content):
        return f"List<{content}>"

    def dict_type(self, key_type, value_type):
        return f"Dict<{key_type}:{value_type}>"

    def method_definition(self, *args):
        visibility = "public"
        name = None
        params = []
        return_type = None
        description = None
        i = 0
        if args[i] in ["public", "private", "protected"]:
            visibility = args[i]
            i += 1
        name = str(args[i])
        i += 1
        if isinstance(args[i], list):
            params = args[i]
            i += 1
        if i < len(args) and args[i].startswith(':'):
            return_type = args[i][1:]
            i += 1
        if i < len(args) and args[i].startswith('{'):
            description = args[i][1:-1]
        return Method(
            name=name,
            visibility=visibility,
            parameters=params,
            return_type=return_type,
            description=description
        )

    def parameter_list(self, *params):
        return list(params)

    def parameter(self, name, type_def, *rest):
        param_name = str(name)
        default_value = None
        if rest and rest[0].startswith('='):
            default_value = rest[0][1:]
        return Parameter(
            name=param_name,
            type=type_def,
            default_value=default_value
        )

    def api_definition(self, http_method, path, *rest):
        params = []
        return_type = None
        description = None
        i = 0
        if i < len(rest) and isinstance(rest[i], list):
            params = rest[i]
            i += 1
        if i < len(rest) and rest[i].startswith(':'):
            return_type = rest[i][1:]
            i += 1
        if i < len(rest) and rest[i].startswith('{'):
            description = rest[i][1:-1]
        return ApiEndpoint(
            http_method=http_method,
            path=path.strip('"\''),
            parameters=params,
            return_type=return_type,
            description=description
        )

    def ui_definition(self, component_type, *rest):
        params = []
        description = None
        i = 0
        if i < len(rest) and isinstance(rest[i], list):
            params = rest[i]
            i += 1
        if i < len(rest) and rest[i].startswith('{'):
            description = rest[i][1:-1]
        return UiComponent(
            component_type=component_type,
            parameters=params,
            description=description
        )

    def relationship_definition(self, source, relationship_type, target, *rest):
        description = None
        if rest and rest[0].startswith('{'):
            description = rest[0][1:-1]
        return Relationship(
            source_entity=source,
            target_entity=target,
            relationship_type=relationship_type,
            description=description
        )
```

## Interpreter

The interpreter coordinates the parsing and transformation of DSL files into domain models that can be used by code generators.

### Interpreter Implementation (interpreter.py)

```python
import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

from parser import DomainForgeParser
from transformer import DomainForgeTransformer
from models import DomainModel, BoundedContext

class DomainForgeInterpreter:
    def __init__(self):
        self.parser = DomainForgeParser()
        self.transformer = DomainForgeTransformer()

    def interpret(self, text: str) -> DomainModel:
        parse_tree = self.parser.parse(text)
        bounded_contexts = self.transformer.transform(parse_tree)
        return DomainModel(bounded_contexts=bounded_contexts)

    def interpret_file(self, file_path: str) -> DomainModel:
        with open(file_path, 'r') as f:
            text = f.read()
        return self.interpret(text)

    def generate_code(self, domain_model: DomainModel, output_dir: str) -> None:
        os.makedirs(output_dir, exist_ok=True)
        backend_dir = os.path.join(output_dir, "backend")
        frontend_dir = os.path.join(output_dir, "frontend")
        os.makedirs(backend_dir, exist_ok=True)
        os.makedirs(frontend_dir, exist_ok=True)
        model_json = domain_model.json(indent=2)
        with open(os.path.join(output_dir, "domain_model.json"), "w") as f:
            f.write(model_json)
        print(f"Domain model saved to {os.path.join(output_dir, 'domain_model.json')}")
        print("Code generation will be implemented in future versions")

    def export_model(self, domain_model: DomainModel, output_file: str) -> None:
        with open(output_file, 'w') as f:
            f.write(domain_model.json(indent=2))
```

## Usage Instructions

### Installation

```bash
pip install domainforge
```

### Basic Usage

1. Create a domain model file:

```domainforge
@Blog {
  #Post {
    id: UUID
    title: String [required]
    content: Text [required]
    published: Boolean = false

    api: GET "/posts"
    ui: Form
  }
}
```

2. Generate your application:

```bash
domainforge generate blog.domainforge --output ./my-blog-app
```

3. Run the generated applications:

```bash
# Backend (FastAPI)
cd my-blog-app/backend
pip install -r requirements.txt
uvicorn src.main:app --reload

# Frontend (React)
cd my-blog-app/frontend
npm install
npm run dev
```
