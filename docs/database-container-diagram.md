# Database Container Diagram

This document provides an overview of the database container using the C4 model. The diagram below describes the main components of the database container, their responsibilities, and interactions.

## Diagram Description

- **Components**:
    - *Database*: Stores application data.
    - *Tables*: Organizes data into rows and columns.
    - *Indexes*: Optimizes data retrieval.
    - *Views*: Provides a virtual table based on the result-set of a query.

## C4 Component Diagram (PlantUML)

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml

' Define system boundary and components
Container_Boundary(database, "Database") {
    Component(database, "Database", "SQLite", "Stores application data")
    Component(tables, "Tables", "Database Tables", "Organizes data into rows and columns")
    Component(indexes, "Indexes", "Database Indexes", "Optimizes data retrieval")
    Component(views, "Views", "Database Views", "Provides a virtual table based on the result-set of a query")
}

' Define relationships between components
Rel(database, tables, "Contains")
Rel(tables, indexes, "Uses")
Rel(tables, views, "Uses")

@enduml
```
