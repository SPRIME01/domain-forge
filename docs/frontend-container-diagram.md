# Frontend Container Diagram

This document provides an overview of the frontend container using the C4 model. The diagram below describes the main components of the frontend container, their responsibilities, and interactions.

## Diagram Description

- **Components**:
    - *AppShell*: The main layout component that provides navigation and consistent structure.
    - *EntityForm*: A standardized way to create and edit entities.
    - *EntityList*: Displays lists of entities with filtering and sorting capabilities.
    - *EntityDetail*: Displays detailed entity information.

## C4 Component Diagram (PlantUML)

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml

' Define system boundary and components
Container_Boundary(frontend, "Frontend") {
    Component(appShell, "AppShell", "React Component", "Provides navigation and consistent structure")
    Component(entityForm, "EntityForm", "React Component", "Standardized way to create and edit entities")
    Component(entityList, "EntityList", "React Component", "Displays lists of entities with filtering and sorting capabilities")
    Component(entityDetail, "EntityDetail", "React Component", "Displays detailed entity information")
}

' Define relationships between components
Rel(appShell, entityForm, "Includes")
Rel(appShell, entityList, "Includes")
Rel(appShell, entityDetail, "Includes")

@enduml
```
