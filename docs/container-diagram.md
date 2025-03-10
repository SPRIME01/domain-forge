# C4 Container Diagram Documentation

This document provides an overview of the container diagram for the project using the C4 model. The diagram below describes the main containers of the system, their responsibilities, and interactions.

## Diagram Description

- **People and Roles**:
    - *User*: A user interacting with the system.

- **Containers**:
    - **Frontend**:
        - User interface for interacting with the application.
        - Technologies: TypeScript/React.

    - **Backend**:
        - Handles business logic, API endpoints, and data processing.
        - Technologies: Python/FastAPI.

    - **Database**:
        - Stores application data.
        - Technologies: SQLite.

## C4 Container Diagram (PlantUML)

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml

' Define external actors
Person(user, "User", "Interacts with the application")

' Define system boundary and containers
System_Boundary(system, "DomainForge System") {
    Container(frontend, "Frontend", "TypeScript/React", "Provides the user interface")
    Container(backend, "Backend", "Python/FastAPI", "Handles business logic and API requests")
    ContainerDb(database, "Database", "SQLite", "Stores application data")
}

' Define relationships between elements
Rel(user, frontend, "Uses", "HTTPS")
Rel(frontend, backend, "Sends requests to", "JSON/HTTPS")
Rel(backend, database, "Reads from and writes to", "SQLAlchemy")

@enduml
```

This diagram adheres to the C4 model, clearly delineating component boundaries and interactions. Adjust the diagram details to better fit your specific project requirements if needed.
