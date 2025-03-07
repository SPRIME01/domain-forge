Feature: DomainForge DSL Interpretation
    As a domain modeler
    I want to write domain models in DomainForge DSL
    So that I can generate code for my domain-driven applications

    Scenario: Basic entity definition
        Given a DomainForge DSL file with the following content
        When the DSL file is interpreted
        Then the resulting domain model should have a context named "Context"
        And the context should have an entity named "Entity"
        And the entity should have a property named "name" of type "String"
