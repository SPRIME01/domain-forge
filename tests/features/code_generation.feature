Feature: Code Generation
  As a developer
  I want to generate domain-driven code
  So that I can quickly implement business requirements

  Background:
    Given the code generation system is initialized
    And the output directory is empty

  Scenario: Generate a domain entity
    When I request generation of a domain entity "Customer"
    And I specify the following properties:
      | name     | type   | required |
      | id       | UUID   | yes      |
      | name     | string | yes      |
      | email    | string | yes      |
      | age      | int    | no       |
      | isActive | bool   | yes      |
    Then a file "customer.py" should be created
    And the file should contain a class "Customer"
    And the class should have all specified properties
    And the class should include validation methods
    And the generated code should follow Python best practices

  Scenario: Generate a repository interface
    When I request generation of a repository for entity "Customer"
    Then a file "customer_repository.py" should be created
    And the file should contain an interface "CustomerRepository"
    And the interface should include CRUD methods
    And the methods should use async/await pattern
    And the generated code should follow Python best practices

  Scenario: Generate a service layer
    When I request generation of a service for entity "Customer"
    Then a file "customer_service.py" should be created
    And the file should contain a class "CustomerService"
    And the class should depend on "CustomerRepository"
    And the class should include business operations
    And the methods should use async/await pattern
    And the generated code should follow Python best practices

  Scenario: Generate domain events
    When I request generation of domain events for entity "Customer"
    Then a file "customer_events.py" should be created
    And the file should contain event classes
    And the events should include "CustomerCreated"
    And the events should include "CustomerUpdated"
    And the events should include "CustomerDeleted"
    And the generated code should follow Python best practices

  Scenario: Generate test files
    When I request generation of tests for entity "Customer"
    Then a test file "test_customer.py" should be created
    And the test file should contain pytest test cases
    And the test cases should cover entity creation
    And the test cases should cover validation logic
    And the test cases should follow best practices for testing
