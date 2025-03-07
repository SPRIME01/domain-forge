"""
Transformer for converting parse trees to domain models.

This module transforms the Lark parse tree into domain model objects that can be
used by the code generators.
"""

from typing import Any, List, Optional, Union, cast

from lark import Token, Transformer, Tree

from .models import (
    ApiEndpoint,
    BoundedContext,
    DomainModel,
    Entity,
    Event,
    Method,
    Module,
    Parameter,
    Property,
    Relationship,
    Repository,
    Role,
    Service,
    UiComponent,
    ValueObject,
)


class DomainForgeTransformer(Transformer):
    """
    Transformer for converting Lark parse trees ito domain model objects.
    """

    def transform(self, tree: Union[Tree, List]) -> DomainModel:
        """Transform the parse tree into a domain model."""
        if isinstance(tree, Tree):
            if tree.data == "start":
                return self.start(tree.children)
            return self.start([tree])
        return self.start(tree)

    def start(self, items: List[Any]) -> DomainModel:
        """Transform the root node into a DomainModel."""
        # Ensure we're working with a list
        if not isinstance(items, list):
            items = [items]

        contexts: List[BoundedContext] = []
        for item in items:
            if isinstance(item, Tree) and item.data == "context_definition":
                ctx = self.context_definition(item.children)
                contexts.append(ctx)
        return DomainModel(bounded_contexts=contexts)

    def context_definition(self, items: List[Tree]) -> BoundedContext:
        """Transform a context definition into a BoundedContext."""
        name: str = str(items[0])

        # Get all the children from the context_children node
        contents: List[Tree] = []
        if len(items) > 1:
            if hasattr(items[1], "data") and items[1].data == "context_children":
                contents = items[1].children

        entities: List[Entity] = []
        value_objects: List[ValueObject] = []
        events: List[Event] = []
        services: List[Service] = []
        repositories: List[Repository] = []
        modules: List[Module] = []
        roles: List[Role] = []
        relationships: List[Relationship] = []

        for item in contents:
            if hasattr(item, "data"):
                if item.data == "entity_definition":
                    entities.append(self.entity_definition(item.children))
                elif item.data == "value_object_definition":
                    value_objects.append(self.value_object_definition(item.children))
                elif item.data == "event_definition":
                    events.append(self.event_definition(item.children))
                elif item.data == "service_definition":
                    services.append(self.service_definition(item.children))
                elif item.data == "repository_definition":
                    repositories.append(self.repository_definition(item.children))
                elif item.data == "module_definition":
                    modules.append(self.module_definition(item.children))
                elif item.data == "role_definition":
                    roles.append(self.role_definition(item.children))
                elif item.data == "relationship_definition":
                    relationships.append(self.relationship_definition(item.children))

        # Add relationships to their source entities
        for rel in relationships:
            source_entity_name: str = rel.source_entity
            for entity in entities:
                if entity.name == source_entity_name:
                    entity.relationships.append(rel)
                    break

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

    def context_children(self, items: List[Tree]) -> List[Tree]:
        """Transform context children into a list of model objects."""
        return items

    def entity_definition(self, items: List[Tree]) -> Entity:
        """Transform an entity definition into an Entity."""
        name: str = str(items[0])

        # Check if we have an inheritance node
        parent: Optional[str] = None
        children_node: Optional[Tree] = None
        if len(items) > 1:
            if hasattr(items[1], "data"):
                if items[1].data == "entity_inheritance":
                    parent = str(items[1].children[0])
                    children_node = items[2] if len(items) > 2 else None
                else:
                    children_node = items[1]
            else:
                children_node = items[1]

        # Transform the children
        properties: List[Property] = []
        methods: List[Method] = []
        apis: List[ApiEndpoint] = []
        uis: List[UiComponent] = []
        relationships: List[Relationship] = []

        if (
            children_node
            and hasattr(children_node, "data")
            and children_node.data == "entity_children"
        ):
            transformed_children: List[
                Union[Property, Method, ApiEndpoint, UiComponent, Relationship]
            ] = self.entity_children(children_node.children)
            for child in transformed_children:
                if isinstance(child, Property):
                    properties.append(child)
                elif isinstance(child, Method):
                    methods.append(child)
                elif isinstance(child, ApiEndpoint):
                    apis.append(child)
                elif isinstance(child, UiComponent):
                    uis.append(child)
                elif isinstance(child, Relationship):
                    relationships.append(child)

        return Entity(
            name=name,
            parent=parent,
            properties=properties,
            methods=methods,
            apis=apis,
            uis=uis,
            relationships=relationships,
        )

    def entity_children(self, items: List[Tree]) -> List[Any]:
        """Transform entity children into a list of model objects."""
        result: List[Any] = []
        for item in items:
            if hasattr(item, "data"):
                if item.data == "property_definition":
                    result.append(self.property_definition(item.children))
                elif item.data == "ui_definition":
                    result.append(self.ui_definition(item.children))
                elif item.data == "api_definition":
                    result.append(self.api_definition(item.children))
                elif item.data == "method_definition":
                    result.append(self.method_definition(item.children))
            else:
                result.append(item)
        return result

    def entity_inheritance(self, items: List[Tree]) -> str:
        """Get the parent entity name."""
        return str(items[0])

    def value_object_definition(self, items: List[Tree]) -> ValueObject:
        """Transform a value object definition into a ValueObject."""
        name: str = str(items[0])
        # Properties are directly nested in value objects
        properties: List[Property] = [
            cast(Property, item) for item in items[1:] if isinstance(item, Property)
        ]

        return ValueObject(
            name=name,
            properties=properties,
        )

    def event_definition(self, items: List[Tree]) -> Event:
        """Transform an event definition into an Event."""
        name: str = str(items[0])
        # Properties are directly nested in events
        properties: List[Property] = [
            cast(Property, item) for item in items[1:] if isinstance(item, Property)
        ]

        return Event(
            name=name,
            properties=properties,
        )

    def service_definition(self, items: List[Tree]) -> Service:
        """Transform a service definition into a Service."""
        name: str = str(items[0])

        # Transform the children
        methods: List[Method] = []
        apis: List[ApiEndpoint] = []

        children_node: Optional[Tree] = items[1] if len(items) > 1 else None

        if (
            children_node
            and hasattr(children_node, "data")
            and children_node.data == "service_children"
        ):
            transformed_children: List[Union[Method, ApiEndpoint]] = (
                self.service_children(children_node.children)
            )
            for child in transformed_children:
                if isinstance(child, Method):
                    methods.append(child)
                elif isinstance(child, ApiEndpoint):
                    apis.append(child)

        return Service(
            name=name,
            methods=methods,
            apis=apis,
        )

    def service_children(self, items: List[Tree]) -> List[Any]:
        """Transform service children into a list of model objects."""
        result: List[Any] = []
        for item in items:
            if hasattr(item, "data"):
                if item.data == "method_definition":
                    result.append(self.method_definition(item.children))
                elif item.data == "api_definition":
                    result.append(self.api_definition(item.children))
            else:
                result.append(item)
        return result

    def repository_definition(self, items: List[Tree]) -> Repository:
        """Transform a repository definition into a Repository."""
        name: str = str(items[0])
        # Methods are directly nested in repositories
        methods: List[Method] = [
            cast(Method, item) for item in items[1:] if isinstance(item, Method)
        ]

        return Repository(
            name=name,
            methods=methods,
        )

    def module_definition(self, items: List[Tree]) -> Module:
        """Transform a module definition into a Module."""
        name: str = str(items[0])
        # The module_children contains the transformed children
        contents: List[Tree] = (
            items[1].children
            if len(items) > 1 and hasattr(items[1], "children")
            else []
        )

        entities: List[Entity] = []
        value_objects: List[ValueObject] = []
        events: List[Event] = []
        services: List[Service] = []
        repositories: List[Repository] = []

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

    def module_children(self, items: List[Tree]) -> List[Tree]:
        """Pass through the children items."""
        return items

    def role_definition(self, items: List[Tree]) -> Role:
        """Transform a role definition into a Role."""
        name: str = str(items[0])
        # Properties are directly nested in roles
        properties: List[Property] = [
            cast(Property, item) for item in items[1:] if isinstance(item, Property)
        ]

        return Role(
            name=name,
            properties=properties,
        )

    def property_definition(self, items: List[Tree]) -> Property:
        """Transform a property definition into a Property."""
        name: str = str(items[0])

        # Get type from type_definition node
        type_def: Tree = items[1]
        type_str: str = "Any"  # Default type

        if hasattr(type_def, "children") and type_def.children:
            simple_type: Tree = type_def.children[0]
            if hasattr(simple_type, "children") and simple_type.children:
                type_str = str(simple_type.children[0])

        # Handle optional default value and constraints
        default_value: Optional[str] = None
        constraints: List[str] = []

        for i in range(2, len(items)):
            if hasattr(items[i], "data"):
                if items[i].data == "property_default":
                    default_value = str(items[i].children[0])
                elif items[i].data == "property_constraint":
                    constraints = [str(c) for c in items[i].children]

        return Property(
            name=name,
            type=type_str,
            default_value=default_value,
            constraints=constraints,
        )

    def _extract_type(self, type_node: Any) -> str:
        """Helper method to extract type strings from type definition nodes."""
        if isinstance(type_node, str):
            return type_node

        if hasattr(type_node, "data"):
            if type_node.data == "simple_type":
                return str(type_node.children[0])
            elif type_node.data == "generic_type":
                container: str = str(type_node.children[0])
                content: str = self._extract_type(type_node.children[1])
                return f"{container}<{content}>"
            elif type_node.data == "list_type":
                content = self._extract_type(type_node.children[0])
                return f"List<{content}>"
            elif type_node.data == "dict_type":
                key = self._extract_type(type_node.children[0])
                value = self._extract_type(type_node.children[1])
                return f"Dict<{key}:{value}>"
            elif hasattr(type_node, "children") and type_node.children:
                return self._extract_type(type_node.children[0])

        return str(type_node)

    def method_definition(self, items: List[Tree]) -> Method:
        """Transform a method definition into a Method."""
        index: int = 0
        visibility: str = "public"

        # Check for optional visibility
        if (
            index < len(items)
            and hasattr(items[index], "data")
            and items[index].data == "visibility"
        ):
            visibility = str(items[index].children[0])
            index += 1

        # Get the method name
        name: str = str(items[index])
        index += 1

        # Get parameters if present
        parameters: List[Parameter] = []
        if (
            index < len(items)
            and hasattr(items[index], "data")
            and items[index].data == "parameter_list"
        ):
            param_items: List[Tree] = items[index].children
            for param in param_items:
                if hasattr(param, "data") and param.data == "parameter":
                    param_name: str = str(param.children[0])
                    param_type_def: Tree = param.children[1]
                    param_type: str = self._extract_type(param_type_def.children[0])
                    param_default: Optional[Any] = None
                    if len(param.children) > 2:
                        param_default = (
                            param.children[2].children[0]
                            if hasattr(param.children[2], "children")
                            else param.children[2]
                        )
                    parameters.append(
                        Parameter(
                            name=param_name,
                            type=param_type,
                            default_value=param_default,
                        )
                    )
            index += 1

        # Get return type if present
        return_type: Optional[str] = None
        if (
            index < len(items)
            and hasattr(items[index], "data")
            and items[index].data == "return_type"
        ):
            type_def: Tree = items[index].children[0]
            return_type = self._extract_type(type_def.children[0])
            index += 1

        # Get description if present
        description: Optional[str] = None
        if (
            index < len(items)
            and hasattr(items[index], "data")
            and items[index].data == "method_body"
        ):
            if len(items[index].children) > 0:
                desc_node: Tree = items[index].children[0]
                description = (
                    str(desc_node.children[0])[1:-1]
                    if hasattr(desc_node, "children")
                    else str(desc_node)
                )

        return Method(
            name=name,
            visibility=visibility,
            parameters=parameters,
            return_type=return_type,
            description=description,
        )

    def visibility(self, items: List[Tree]) -> str:
        """Get the visibility value."""
        return str(items[0])

    def return_type(self, items: List[Tree]) -> str:
        """Get the return type."""
        return str(items[0])

    def method_body(self, items: List[Tree]) -> Optional[str]:
        """Get the method body description if present."""
        if items and hasattr(items[0], "data") and items[0].data == "description":
            return (
                str(items[0].children[0])[1:-1]
                if hasattr(items[0], "children")
                else str(items[0])
            )
        return None

    def parameter_list(self, items: List[Tree]) -> List[Tree]:
        """Transform a parameter list into a list of Parameters."""
        return items

    def parameter(self, items: List[Tree]) -> Parameter:
        """Transform a parameter definition into a Parameter."""
        name: str = str(items[0])

        # Handle the type definition which is now a nested node
        type_def: Tree = items[1]
        type_str: str = (
            str(type_def.children[0])
            if hasattr(type_def, "children")
            else str(type_def)
        )

        # Handle optional default value
        default_value: Optional[Any] = None
        if (
            len(items) > 2
            and hasattr(items[2], "data")
            and items[2].data == "parameter_default"
        ):
            default_value = items[2].children[0]

        return Parameter(
            name=name,
            type=type_str,
            default_value=default_value,
        )

    def parameter_default(self, items: List[Tree]) -> Any:
        """Get the parameter default value."""
        return items[0]

    def type_definition(self, items: List[Tree]) -> Tree:
        """Transform a type definition into a type string."""
        # This should return the type node to be processed by the parent node
        return items[0]

    def simple_type(self, items: List[Tree]) -> str:
        """Handle a simple type."""
        return str(items[0])

    def generic_type(self, items: List[Tree]) -> str:
        """Handle a generic type."""
        return f"{str(items[0])}<{str(items[1])}>"

    def list_type(self, items: List[Tree]) -> str:
        """Handle a list type."""
        return f"List<{str(items[0])}>"

    def dict_type(self, items: List[Tree]) -> str:
        """Handle a dictionary type."""
        return f"Dict<{str(items[0])}:{str(items[1])}>"

    def property_default(self, items: List[Tree]) -> Any:
        """Get the property default value."""
        return items[0]

    def property_constraint(self, items: List[Tree]) -> List[str]:
        """Get the property constraints."""
        return [str(item) for item in items]

    def constraint(self, items: List[Tree]) -> str:
        """Transform a constraint into a string."""
        return str(items[0])

    def min_constraint(self, items: List[Tree]) -> str:
        """Handle min constraint."""
        return f"min:{str(items[1])}"

    def max_constraint(self, items: List[Tree]) -> str:
        """Handle max constraint."""
        return f"max:{str(items[1])}"

    def pattern_constraint(self, items: List[Tree]) -> str:
        """Handle pattern constraint."""
        return f"pattern:{str(items[1])}"

    def fk_constraint(self, items: List[Tree]) -> str:
        """Handle foreign key constraint."""
        return f"foreign_key:{str(items[1])}"

    def default_value(self, items: List[Tree]) -> Any:
        """Transform a default value into its Python equivalent."""
        return items[0]

    def list_value(self, items: List[Tree]) -> List[Any]:
        """Transform a list value."""
        if items and hasattr(items[0], "data") and items[0].data == "value_list":
            return items[0].children
        return []

    def value_list(self, items: List[Tree]) -> List[Any]:
        """Transform a value list into a Python list."""
        return items

    def value(self, items: List[Tree]) -> Any:
        """Transform a value into its Python equivalent."""
        item = items[0]
        if isinstance(item, Token):
            if item.type == "INT":
                return int(item.value)
            elif item.type == "FLOAT":
                return float(item.value)
            elif item.type == "STRING":
                return item.value[1:-1]  # Remove quotes
            elif item.type == "IDENTIFIER":
                if item.value.lower() == "true":
                    return True
                elif item.value.lower() == "false":
                    return False
                elif item.value.lower() == "null":
                    return None
                return item.value
        return item

    def relationship_definition(self, items: List[Tree]) -> Relationship:
        """Transform a relationship definition into a Relationship."""
        source: str = (
            items[0].children[0] if hasattr(items[0], "children") else str(items[0])
        )
        target: str = (
            items[2].children[0] if hasattr(items[2], "children") else str(items[2])
        )
        relationship_type: str = str(items[1])

        description: Optional[str] = None
        if (
            len(items) > 3
            and hasattr(items[3], "data")
            and items[3].data == "relationship_desc"
        ):
            if len(items[3].children) > 0:
                desc: Tree = items[3].children[0]
                description = (
                    str(desc.children[0])[1:-1]
                    if hasattr(desc, "children")
                    else str(desc)
                )

        return Relationship(
            source_entity=source,
            target_entity=target,
            relationship_type=relationship_type,
            description=description,
        )

    def source_entity(self, items: List[Tree]) -> str:
        """Get the source entity name."""
        return str(items[0])

    def target_entity(self, items: List[Tree]) -> str:
        """Get the target entity name."""
        return str(items[0])

    def relationship_desc(self, items: List[Tree]) -> Optional[Tree]:
        """Get the relationship description if present."""
        if items and hasattr(items[0], "data") and items[0].data == "description":
            return items[0]
        return None

    def description(self, items: List[Tree]) -> str:
        """Transform a description into a string."""
        return str(items[0])[1:-1]  # Remove quotes

    def api_definition(self, items: List[Tree]) -> ApiEndpoint:
        """Transform an API definition into an ApiEndpoint."""
        http_method: str = str(items[0])
        path: str = str(items[1])[1:-1]  # Remove quotes from path

        parameters: List[Parameter] = []
        return_type: Optional[str] = None
        description: Optional[str] = None

        index: int = 2

        # Handle optional parameters
        if (
            index < len(items)
            and hasattr(items[index], "data")
            and items[index].data == "api_params"
        ):
            if (
                len(items[index].children) > 0
                and hasattr(items[index].children[0], "data")
                and items[index].children[0].data == "parameter_list"
            ):
                parameters = [
                    cast(Parameter, p) for p in items[index].children[0].children
                ]
            index += 1

        # Handle optional return type
        if (
            index < len(items)
            and hasattr(items[index], "data")
            and items[index].data == "api_return"
        ):
            type_def: Tree = items[index].children[0]
            return_type = (
                str(type_def.children[0])
                if hasattr(type_def, "children")
                else str(type_def)
            )
            index += 1

        # Handle optional description
        if (
            index < len(items)
            and hasattr(items[index], "data")
            and items[index].data == "api_desc"
        ):
            if len(items[index].children) > 0:
                desc: Tree = items[index].children[0]
                description = (
                    str(desc.children[0])[1:-1]
                    if hasattr(desc, "children")
                    else str(desc)
                )

        return ApiEndpoint(
            http_method=http_method,
            path=path,
            parameters=parameters,
            return_type=return_type,
            description=description,
        )

    def api_params(self, items: List[Tree]) -> List[Tree]:
        """Get the API parameters."""
        return items

    def api_return(self, items: List[Tree]) -> Tree:
        """Get the API return type."""
        return items[0]

    def api_desc(self, items: List[Tree]) -> Optional[Tree]:
        """Get the API description."""
        return items[0] if items else None

    def ui_definition(self, items: List[Tree]) -> UiComponent:
        """Transform a UI definition into a UiComponent."""
        component_type: str = str(items[0])

        parameters: List[Parameter] = []
        description: Optional[str] = None

        index: int = 1

        # Handle optional parameters
        if (
            index < len(items)
            and hasattr(items[index], "data")
            and items[index].data == "ui_params"
        ):
            if (
                len(items[index].children) > 0
                and hasattr(items[index].children[0], "data")
                and items[index].children[0].data == "parameter_list"
            ):
                parameters = items[index].children[0].children
            index += 1

        # Handle optional description
        if (
            index < len(items)
            and hasattr(items[index], "data")
            and items[index].data == "ui_desc"
        ):
            if len(items[index].children) > 0:
                desc: Tree = items[index].children[0]
                description = (
                    str(desc.children[0])[1:-1]
                    if hasattr(desc, "children")
                    else str(desc)
                )

        return UiComponent(
            component_type=component_type,
            parameters=parameters,
            description=description,
        )

    def ui_params(self, items: List[Tree]) -> List[Tree]:
        """Get the UI parameters."""
        return items

    def ui_desc(self, items: List[Tree]) -> Optional[Tree]:
        """Get the UI description."""
        return items[0] if items else None

    # Break down complex functions like context_definition and entity_definition
    def context_definition(self, ctx: List[Tree]) -> BoundedContext:
        """Transform a context definition into a BoundedContext."""
        name: str = str(ctx[0])

        # Get all the children from the context_children node
        contents: List[Tree] = []
        if len(ctx) > 1:
            if hasattr(ctx[1], "data") and ctx[1].data == "context_children":
                contents = ctx[1].children

        entities: List[Entity] = []
        value_objects: List[ValueObject] = []
        events: List[Event] = []
        services: List[Service] = []
        repositories: List[Repository] = []
        modules: List[Module] = []
        roles: List[Role] = []
        relationships: List[Relationship] = []

        for item in contents:
            if hasattr(item, "data"):
                if item.data == "entity_definition":
                    entities.append(self.entity_definition(item.children))
                elif item.data == "value_object_definition":
                    value_objects.append(self.value_object_definition(item.children))
                elif item.data == "event_definition":
                    events.append(self.event_definition(item.children))
                elif item.data == "service_definition":
                    services.append(self.service_definition(item.children))
                elif item.data == "repository_definition":
                    repositories.append(self.repository_definition(item.children))
                elif item.data == "module_definition":
                    modules.append(self.module_definition(item.children))
                elif item.data == "role_definition":
                    roles.append(self.role_definition(item.children))
                elif item.data == "relationship_definition":
                    relationships.append(self.relationship_definition(item.children))

        # Add relationships to their source entities
        for rel in relationships:
            source_entity_name: str = rel.source_entity
            for entity in entities:
                if entity.name == source_entity_name:
                    entity.relationships.append(rel)
                    break

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

    # Fix append type errors
    def entity_definition(self, items: List[Tree]) -> Entity:
        """Transform an entity definition into an Entity."""
        name: str = str(items[0])

        # Check if we have an inheritance node
        parent: Optional[str] = None
        children_node: Optional[Tree] = None
        if len(items) > 1:
            if hasattr(items[1], "data"):
                if items[1].data == "entity_inheritance":
                    parent = str(items[1].children[0])
                    children_node = items[2] if len(items) > 2 else None
                else:
                    children_node = items[1]
            else:
                children_node = items[1]

        # Transform the children
        properties: List[Property] = []
        methods: List[Method] = []
        apis: List[ApiEndpoint] = []
        uis: List[UiComponent] = []
        relationships: List[Relationship] = []

        if (
            children_node
            and hasattr(children_node, "data")
            and children_node.data == "entity_children"
        ):
            transformed_children: List[Any] = self.entity_children(
                children_node.children
            )
            for child in transformed_children:
                if isinstance(child, Property):
                    properties.append(child)
                elif isinstance(child, Method):
                    methods.append(child)
                elif isinstance(child, ApiEndpoint):
                    apis.append(child)
                elif isinstance(child, UiComponent):
                    uis.append(child)
                elif isinstance(child, Relationship):
                    relationships.append(child)

        return Entity(
            name=name,
            parent=parent,
            properties=properties,
            methods=methods,
            apis=apis,
            uis=uis,
            relationships=relationships,
        )

    # Fix return type issues
    def some_function(self) -> str:
        """Ensure it always returns a string."""
        some_value: Optional[str] = None  # Example value
        return some_value or ""  # Ensure it always returns a string

