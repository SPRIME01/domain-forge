"""
Domain models for the DomainForge parser.

These models represent the parsed structure of a domain model specification
and are used to generate code for both backend and frontend applications.
"""

from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel, Field


class Parameter(BaseModel):
    """
    Represents a parameter in a method signature or API endpoint.
    """
    name: str
    type: str
    default_value: Optional[Any] = None


class Property(BaseModel):
    """
    Represents a property/attribute of an entity, value object, etc.
    """
    name: str
    type: str
    default_value: Optional[Any] = None
    constraints: List[str] = Field(default_factory=list)


class Method(BaseModel):
    """
    Represents a method/function in an entity or service.
    """
    name: str
    visibility: str = "public"
    parameters: List[Parameter] = Field(default_factory=list)
    return_type: Optional[str] = None
    description: Optional[str] = None


class ApiEndpoint(BaseModel):
    """
    Represents a REST API endpoint definition.
    """
    http_method: str
    path: str
    parameters: List[Parameter] = Field(default_factory=list)
    return_type: Optional[str] = None
    description: Optional[str] = None


class UiComponent(BaseModel):
    """
    Represents a UI component definition.
    """
    component_type: str
    parameters: List[Parameter] = Field(default_factory=list)
    description: Optional[str] = None


class Relationship(BaseModel):
    """
    Represents a relationship between entities.
    """
    source_entity: str
    target_entity: str
    relationship_type: str
    description: Optional[str] = None


class Entity(BaseModel):
    """
    Represents a domain entity (aggregate root).
    """
    name: str
    parent: Optional[str] = None
    properties: List[Property] = Field(default_factory=list)
    methods: List[Method] = Field(default_factory=list)
    apis: List[ApiEndpoint] = Field(default_factory=list)
    uis: List[UiComponent] = Field(default_factory=list)
    relationships: List[Relationship] = Field(default_factory=list)


class ValueObject(BaseModel):
    """
    Represents a value object in the domain.
    """
    name: str
    properties: List[Property] = Field(default_factory=list)


class Event(BaseModel):
    """
    Represents a domain event.
    """
    name: str
    properties: List[Property] = Field(default_factory=list)


class Service(BaseModel):
    """
    Represents a domain service.
    """
    name: str
    methods: List[Method] = Field(default_factory=list)
    apis: List[ApiEndpoint] = Field(default_factory=list)


class Repository(BaseModel):
    """
    Represents a repository for accessing entities.
    """
    name: str
    methods: List[Method] = Field(default_factory=list)


class Role(BaseModel):
    """
    Represents a role or actor in the domain.
    """
    name: str
    properties: List[Property] = Field(default_factory=list)


class Module(BaseModel):
    """
    Represents a module or package in the domain.
    """
    name: str
    entities: List[Entity] = Field(default_factory=list)
    value_objects: List[ValueObject] = Field(default_factory=list)
    events: List[Event] = Field(default_factory=list)
    services: List[Service] = Field(default_factory=list)
    repositories: List[Repository] = Field(default_factory=list)


class BoundedContext(BaseModel):
    """
    Represents a bounded context in the domain.
    """
    name: str
    entities: List[Entity] = Field(default_factory=list)
    value_objects: List[ValueObject] = Field(default_factory=list)
    events: List[Event] = Field(default_factory=list)
    services: List[Service] = Field(default_factory=list)
    repositories: List[Repository] = Field(default_factory=list)
    modules: List[Module] = Field(default_factory=list)
    roles: List[Role] = Field(default_factory=list)


class DomainModel(BaseModel):
    """
    Represents the complete domain model.
    """
    bounded_contexts: List[BoundedContext] = Field(default_factory=list)
