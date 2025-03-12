# Backend Container Diagram

This document provides an overview of the backend container using the C4 model. The diagram below describes the main components of the backend container, their responsibilities, and interactions.

## Diagram Description

- **Components**:
  - _API Controller_: Handles incoming HTTP requests and routes them to the appropriate service.
  - _Service Layer_: Contains business logic and orchestrates interactions between repositories and other services.
  - _Repository Layer_: Manages data access and persistence.
  - _Domain Model_: Represents the core business entities and logic.

## C4 Component Diagram (PlantUML)

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml

' Define system boundary and components
Container_Boundary(backend, "Backend") {
    Component(apiController, "API Controller", "FastAPI", "Handles incoming HTTP requests and routes them to the appropriate service")
    Component(serviceLayer, "Service Layer", "Python Module", "Contains business logic and orchestrates interactions between repositories and other services")
    Component(repositoryLayer, "Repository Layer", "Python Module", "Manages data access and persistence")
    Component(domainModel, "Domain Model", "Python Module", "Represents the core business entities and logic")
}

' Define relationships between components
Rel(apiController, serviceLayer, "Calls")
Rel(serviceLayer, repositoryLayer, "Uses")
Rel(serviceLayer, domainModel, "Uses")
Rel(repositoryLayer, domainModel, "Uses")

@enduml
```
