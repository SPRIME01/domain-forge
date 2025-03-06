"""
Transformer for converting parse trees to domain models.

This module transforms the Lark parse tree into domain model objects that can be
used by the code generators.
"""

from typing import Any, Dict, List, Optional, Union
from lark import Transformer, Tree, Token
from .models import (
    Parameter,
    Property,
    Method,
    ApiEndpoint,
    UiComponent,
    Relationship,
    Entity,
    ValueObject,
    Event,
    Service,
    Repository,
    Role,
    Module,
    BoundedContext,
    DomainModel,
)


class DomainForgeTransformer(Transformer):
    """
    Transformer for converting Lark parse trees into domain model objects.
    """

    def start(self, items: List[Tree]) -> DomainModel:
        """Transform the root node into a DomainModel."""
        return DomainModel(bounded_contexts=items)

    def context_definition(self, items: List[Tree]) -> BoundedContext:
        """Transform a context definition into a BoundedContext."""
        name = str(items[0])
        contents = items[1:]

        entities = []
        value_objects = []
        events = []
        services = []
        repositories = []
        modules = []
        roles = []

        for item in contents:
            if isinstance(item, Entity):
                entities.append(item)
            elif isinstance(item, ValueObject):
                value_objects.append(item)
            elif isinstance(item, Event):
                events.append(item)
            elif isinstance(item, Service):
                services.append(item)
            elif isinstance(item, Repository):
                repositories.append(item)
            elif isinstance(item, Module):
                modules.append(item)
            elif isinstance(item, Role):
                roles.append(item)

        return BoundedContext(
            name=name,
            entities=entities,
            value_objects=value_objects,
            events=events,
            services=services,
            repositories=repositories,
            modules=modules,
            roles=roles,
        )

    def entity_definition(self, items: List[Tree]) -> Entity:
        """Transform an entity definition into an Entity."""
        name = str(items[0])
        parent = str(items[1]) if len(items) > 2 else None
        contents = items[-1] if len(items) > 2 else items[1]

        properties = []
        methods = []
        apis = []
        uis = []
        relationships = []

        for item in contents:
            if isinstance(item, Property):
                properties.append(item)
            elif isinstance(item, Method):
                methods.append(item)
            elif isinstance(item, ApiEndpoint):
                apis.append(item)
            elif isinstance(item, UiComponent):
                uis.append(item)
            elif isinstance(item, Relationship):
                relationships.append(item)

        return Entity(
            name=name,
            parent=parent,
            properties=properties,
            methods=methods,
            apis=apis,
            uis=uis,
            relationships=relationships,
        )

    def value_object_definition(self, items: List[Tree]) -> ValueObject:
        """Transform a value object definition into a ValueObject."""
        name = str(items[0])
        properties = items[1] if len(items) > 1 else []

        return ValueObject(
            name=name,
            properties=properties,
        )

    def event_definition(self, items: List[Tree]) -> Event:
        """Transform an event definition into an Event."""
        name = str(items[0])
        properties = items[1] if len(items) > 1 else []

        return Event(
            name=name,
            properties=properties,
        )

    def service_definition(self, items: List[Tree]) -> Service:
        """Transform a service definition into a Service."""
        name = str(items[0])
        contents = items[1] if len(items) > 1 else []

        methods = []
        apis = []

        for item in contents:
            if isinstance(item, Method):
                methods.append(item)
            elif isinstance(item, ApiEndpoint):
                apis.append(item)

        return Service(
            name=name,
            methods=methods,
            apis=apis,
        )

    def repository_definition(self, items: List[Tree]) -> Repository:
        """Transform a repository definition into a Repository."""
        name = str(items[0])
        methods = items[1] if len(items) > 1 else []

        return Repository(
            name=name,
            methods=methods,
        )

    def module_definition(self, items: List[Tree]) -> Module:
        """Transform a module definition into a Module."""
        name = str(items[0])
        contents = items[1] if len(items) > 1 else []

        entities = []
        value_objects = []
        events = []
        services = []
        repositories = []

        for item in contents:
            if isinstance(item, Entity):
                entities.append(item)
            elif isinstance(item, ValueObject):
                value_objects.append(item)
            elif isinstance(item, Event):
                events.append(item)
            elif isinstance(item, Service):
                services.append(item)
            elif isinstance(item, Repository):
                repositories.append(item)

        return Module(
            name=name,
            entities=entities,
            value_objects=value_objects,
            events=events,
            services=services,
            repositories=repositories,
        )

    def property_definition(self, items: List[Tree]) -> Property:
        """Transform a property definition into a Property."""
        name = str(items[0])
        type_ = str(items[1])
        default_value = items[2] if len(items) > 2 else None
        constraints = items[3] if len(items) > 3 else []

        return Property(
            name=name,
            type=type_,
            default_value=default_value,
            constraints=constraints,
        )

    def method_definition(self, items: List[Tree]) -> Method:
        """Transform a method definition into a Method."""
        visibility = str(items[0]) if str(items[0]) in ["public", "private", "protected"] else "public"
        if visibility != "public":
            items = items[1:]

        name = str(items[0])
        parameters = items[1] if len(items) > 1 and isinstance(items[1], list) else []
        return_type = str(items[2]) if len(items) > 2 else None
        description = str(items[3]) if len(items) > 3 else None

        return Method(
            name=name,
            visibility=visibility,
            parameters=parameters,
            return_type=return_type,
            description=description,
        )

    def parameter(self, items: List[Tree]) -> Parameter:
        """Transform a parameter definition into a Parameter."""
        name = str(items[0])
        type_ = str(items[1])
        default_value = items[2] if len(items) > 2 else None

        return Parameter(
            name=name,
            type=type_,
            default_value=default_value,
        )

    def type_definition(self, items: List[Tree]) -> str:
        """Transform a type definition into a type string."""
        if len(items) == 1:  # Simple type
            return str(items[0])
        elif len(items) == 2:  # Generic type
            return f"{items[0]}<{items[1]}>"
        else:  # Dictionary type
            return f"Dict<{items[1]}, {items[2]}>"

    def value(self, items: List[Tree]) -> Any:
        """Transform a value into its Python equivalent."""
        item = items[0]
        if isinstance(item, Token):
            if item.type == "INT":
                return int(item)
            elif item.type == "FLOAT":
                return float(item)
            elif item.type == "STRING":
                return str(item)[1:-1]  # Remove quotes
            elif item.type == "IDENTIFIER":
                if str(item).lower() == "true":
                    return True
                elif str(item).lower() == "false":
                    return False
                elif str(item).lower() == "null":
                    return None
                return str(item)
        return item

    def api_definition(self, items: List[Tree]) -> ApiEndpoint:
        """Transform an API definition into an ApiEndpoint."""
        http_method = str(items[0])
        path = str(items[1])
        parameters = items[2] if len(items) > 2 and isinstance(items[2], list) else []
        return_type = str(items[3]) if len(items) > 3 else None
        description = str(items[4]) if len(items) > 4 else None

        return ApiEndpoint(
            http_method=http_method,
            path=path,
            parameters=parameters,
            return_type=return_type,
            description=description,
        )

    def ui_definition(self, items: List[Tree]) -> UiComponent:
        """Transform a UI definition into a UiComponent."""
        component_type = str(items[0])
        parameters = items[1] if len(items) > 1 and isinstance(items[1], list) else []
        description = str(items[2]) if len(items) > 2 else None

        return UiComponent(
            component_type=component_type,
            parameters=parameters,
            description=description,
        )
