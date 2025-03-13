Feature: Plugin Template System
  As a developer using DomainForge
  I want to use custom code generation templates
  So that I can generate code in my preferred style and framework

  Background:
    Given I have installed the example template plugin
    And I have a domain model file "user.df" with content:
      """
      entity User {
        id: UUID
        name: string
        email: string
        age?: number
      }
      """

  Scenario: Generate backend code with custom template
    When I run "domainforge generate user.df --template example-template --backend fastapi"
    Then the output should contain FastAPI entity code
    And the generated code should contain "class User(BaseModel):"
    And the generated code should contain "id: UUID"
    And the generated code should contain "age: Optional[int]"

  Scenario: Generate frontend code with custom template
    When I run "domainforge generate user.df --template example-template --frontend react"
    Then the output should contain React component code
    And the generated code should contain "interface UserProps"
    And the generated code should contain "age?: number"

  Scenario: List available templates
    When I run "domainforge templates list"
    Then the output should contain "example-template"
    And the output should show supported frameworks:
      | Framework | Templates           |
      | FastAPI   | entity.py.j2       |
      | React     | Entity.tsx.j2      |

  Scenario: Generate with invalid template
    When I run "domainforge generate user.df --template nonexistent"
    Then the command should fail with error "Template plugin 'nonexistent' not found"

  Scenario: Generate with invalid framework
    When I run "domainforge generate user.df --template example-template --backend invalid"
    Then the command should fail with error "Framework 'invalid' not supported by template 'example-template'"
