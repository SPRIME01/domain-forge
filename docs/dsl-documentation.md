# DomainForge DSL Specification

This document provides a comprehensive specification for the DomainForge Domain-Specific Language (DSL), designed for generating full-stack applications with a Python backend and TypeScript frontend based on clean architecture and Domain-Driven Design (DDD) principles.

## Table of Contents

1. [Overview](#overview)
2. [Core Concepts](#core-concepts)
3. [Grammar and Syntax](#grammar-and-syntax)
   - [Basic Structure](#basic-structure)
   - [Bounded Contexts](#bounded-contexts)
   - [Domain Elements](#domain-elements)
   - [Properties and Types](#properties-and-types)
   - [Methods and Parameters](#methods-and-parameters)
   - [Relationships](#relationships)
   - [API Endpoints](#api-endpoints)
   - [UI Components](#ui-components)
4. [Complete Grammar Reference](#complete-grammar-reference)
5. [Implementation Details](#implementation-details)
   - [Parser](#parser)
   - [Transformer](#transformer)
   - [Interpreter](#interpreter)
6. [Usage Instructions](#usage-instructions)
   - [Installation](#installation)
   - [Basic Usage](#basic-usage)
   - [Advanced Examples](#advanced-examples)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)
9. [API Reference](#api-reference)

## Overview

DomainForge DSL is a specialized language that enables you to define your domain model in a clear, structured manner. It bridges the gap between domain modeling and implementation by automatically generating both backend and frontend code that adheres to clean architecture principles.

The DSL supports a wide range of Domain-Driven Design concepts and provides a concise way to express complex domain models, their relationships, API endpoints, and UI components.

## Core Concepts

DomainForge DSL is built around the following core concepts from Domain-Driven Design:

| Concept | Symbol | Description | Example |
|---------|--------|-------------|---------|
| Bounded Context | `@` | A logical boundary for a business domain | `@ECommerce { ... }` |
| Entity | `#` | An object with identity and lifecycle | `#Product { ... }` |
| Value Object | `%` | An immutable object with no identity | `%Address { ... }` |
| Event | `^` | A domain event representing something that happened | `^OrderPlaced { ... }` |
| Service | `>>` | A stateless service providing business operations | `>>PaymentService { ... }` |
| Repository | `$` | A mechanism for storing and retrieving domain objects | `$ProductRepository { ... }` |
| Module | `*` | A logical grouping of related domain elements | `*Catalog { ... }` |
| Role | `&` | A user role or actor in the system | `&Administrator { ... }` |

## Grammar and Syntax

### Basic Structure

The DSL uses a hierarchical structure with each element defined by a symbol prefix followed by a name and a block of content enclosed in curly braces:

```
@BoundedContext {
  #Entity {
    property: Type
    method() {}
  }
}
```

### Bounded Contexts

Bounded contexts are the top-level organizational unit in DomainForge DSL:

```
@ECommerce {
  // Domain elements like entities, value objects, services, etc.
}

@CustomerSupport {
  // Another bounded context with its own domain elements
}
```

### Domain Elements

DomainForge DSL supports various domain elements, each with its own syntax:

#### Entities

```
#Product {
  id: UUID [required]
  name: String [required, minLength:3, maxLength:100]
  price: Decimal [required]
  description: Text
  category: Category

  activate() {}
  deactivate() {}

  api: GET "/products/{id}"
  ui: Form
}
```

#### Value Objects

```
%Address {
  street: String [required]
  city: String [required]
  state: String [required]
  zipCode: String [required, pattern:"\\d{5}(-\\d{4})?"]
}
```

#### Events

```
^OrderPlaced {
  orderId: UUID [required]
  customerId: UUID [required]
  orderItems: List<OrderItem> [required]
  totalAmount: Decimal [required]
  timestamp: DateTime = "new Date()"
}
```

#### Services

```
>>PaymentService {
  processPayment(orderId: UUID, amount: Decimal, paymentMethod: PaymentMethod): Boolean {
    "Process a payment for an order"
  }

  refundPayment(orderId: UUID, amount: Decimal): Boolean {
    "Refund payment for an order"
  }

  api: POST "/payments/process"
  api: POST "/payments/refund"
}
```

#### Repositories

```
$ProductRepository {
  findByCategory(categoryId: UUID): List<Product> {
    "Find all products in a specific category"
  }

  findFeatured(): List<Product> {
    "Find featured products"
  }
}
```

#### Modules

```
*Catalog {
  #Product {
    // Product entity definition
  }

  #Category {
    // Category entity definition
  }

  >>ProductService {
    // Product service definition
  }
}
```

#### Roles

```
&Administrator {
  permissions: List<String> = ["CREATE", "READ", "UPDATE", "DELETE"]
  accessLevel: Integer = 100
}
```

### Properties and Types

Properties are defined with the format `name: Type` and can include optional default values and constraints:

```
username: String [required, minLength:3, maxLength:50]
email: String [required, pattern:"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"]
age: Integer [min:18, max:120] = 21
isActive: Boolean = true
registrationDate: DateTime = "new Date()"
```

#### Supported Basic Types

- `String`: Text values
- `Text`: Longer text values
- `Integer`: Whole numbers
- `Decimal`: Decimal numbers
- `Boolean`: True/false values
- `DateTime`: Date and time values
- `UUID`: Universally unique identifiers
- Custom types (must be defined elsewhere in the domain model)

#### Collection Types

- `List<T>`: A list of elements of type T
- `Dict<K,V>`: A dictionary with keys of type K and values of type V

#### Optional Types

Append `?` to a type to make it optional:
```
description: Text?  // Optional text
```

#### Constraints

Constraints can be applied to properties using square brackets:

- `[required]`: Property is mandatory
- `[unique]`: Property must have a unique value
- `[min:n]`: Minimum value (for numbers) or length (for strings)
- `[max:n]`: Maximum value (for numbers) or length (for strings)
- `[pattern:"regex"]`: Regular expression pattern (for strings)
- `[foreign_key:Entity]`: References another entity

### Methods and Parameters

Methods are defined with the format `name(parameters): ReturnType`:

```
calculateDiscount(amount: Decimal, userType: String): Decimal {
  "Calculate discount based on amount and user type"
}
```

Parameters follow the same pattern as properties: `name: Type` with optional default values.

### Relationships

Relationships between entities are defined with a relationship symbol:

```
Order -> OrderItem  // One-to-many relationship
Customer <-> Address  // Bidirectional relationship
Product -- Category  // Association
User => Role  // Many-to-many relationship
```

| Symbol | Meaning | Description |
|--------|---------|-------------|
| `->` | One-to-many | Parent entity has many child entities |
| `<->` | Bidirectional | Both entities reference each other |
| `--` | Association | Simple association between entities |
| `=>` | Many-to-many | Many-to-many relationship |
| `.` | Composition | Strong ownership, child cannot exist without parent |
| `::` | Implementation | Entity implements an interface or role |
| `/` | Inheritance | Entity inherits from another entity |

### API Endpoints

API endpoints are defined with the format `api: METHOD "path"`:

```
api: GET "/users"
api: GET "/users/{id}"
api: POST "/users" (user: UserDTO): User
api: PUT "/users/{id}" (user: UserDTO): User
api: DELETE "/users/{id}"
```

The format supports:
- HTTP Method: `GET`, `POST`, `PUT`, `DELETE`, `PATCH`
- Path: URL path, can include path parameters in curly braces
- Parameters: Optional input parameters in parentheses
- Return Type: Optional return type after a colon
- Description: Optional description in curly braces

### UI Components

UI components are defined with the format `ui: ComponentType`:

```
ui: Form
ui: Table
ui: Card (title: String = "Details")
ui: Detail
ui: List
```

Advanced UI components with parameters and custom layouts:

```
ui: Form (
  labelPosition: "top",
  submitButtonText: "Save User"
)

ui: Container (
  maxWidth: "1200px",
  margin: "0 auto"
) {
  "Main content container"
}
```

## Complete Grammar Reference

```lark
%import common.WS
%import common.INT
%import common.FLOAT
%import common.WORD
%import common.ESCAPED_STRING
%ignore WS

MODIFIER: "!" | "~" | "?"
ENTITY_SYMBOL: "#" | "%" | "^" | ">>" | "&" | "@" | "$" | "*"
RELATIONSHIP_SYMBOL: "=>" | "<->" | "--" | "->" | "." | "::" | "/"
HTTP_METHOD: "GET" | "POST" | "PUT" | "DELETE" | "PATCH"
UI_COMPONENT: "Form" | "Table" | "Card" | "Detail" | "List" | "Container" | "Grid" | "Panel"
VISIBILITY: "public" | "private" | "protected"
LPAREN: "("
RPAREN: ")"
LSQBRACKET: "["
RSQBRACKET: "]"
LCURLYBRACE: "{"
RCURLYBRACE: "}"
LANGLED: "<"
RANGLED: ">"
ITEM_SEPARATOR: ","
COLON: ":"
COMMENT: /\/\/[^\n]*/ | /\/\*[\s\S]*?\*\//
%ignore COMMENT
IDENTIFIER: /[a-zA-Z_][a-zA-Z0-9_]*/
STRING: ESCAPED_STRING

start: context_definition+
context_definition: "@" IDENTIFIER LCURLYBRACE (entity_definition | value_object_definition | event_definition | service_definition | repository_definition | module_definition | role_definition)* RCURLYBRACE
entity_definition: "#" IDENTIFIER (COLON IDENTIFIER)? LCURLYBRACE (property_definition | method_definition | api_definition | ui_definition)* RCURLYBRACE
value_object_definition: "%" IDENTIFIER LCURLYBRACE property_definition* RCURLYBRACE
event_definition: "^" IDENTIFIER LCURLYBRACE property_definition* RCURLYBRACE
service_definition: ">>" IDENTIFIER LCURLYBRACE (method_definition | api_definition)* RCURLYBRACE
repository_definition: "$" IDENTIFIER LCURLYBRACE method_definition* RCURLYBRACE
module_definition: "*" IDENTIFIER LCURLYBRACE (entity_definition | value_object_definition | event_definition | service_definition | repository_definition)* RCURLYBRACE
role_definition: "&" IDENTIFIER LCURLYBRACE property_definition* RCURLYBRACE
property_definition: IDENTIFIER COLON type_definition (EQUALS default_value)? (LSQBRACKET constraint (ITEM_SEPARATOR constraint)* RSQBRACKET)?
type_definition: simple_type | generic_type | list_type | dict_type | optional_type
simple_type: IDENTIFIER
generic_type: IDENTIFIER LANGLED IDENTIFIER RANGLED
list_type: "List" LANGLED type_definition RANGLED
dict_type: "Dict" LANGLED type_definition COLON type_definition RANGLED
optional_type: type_definition "?"
method_definition: (VISIBILITY)? IDENTIFIER LPAREN parameter_list? RPAREN (COLON type_definition)? (LCURLYBRACE description? RCURLYBRACE)?
parameter_list: parameter (ITEM_SEPARATOR parameter)*
parameter: IDENTIFIER COLON type_definition (EQUALS default_value)?
default_value: INT | FLOAT | STRING | IDENTIFIER | LSQBRACKET value_list? RSQBRACKET
value_list: value (ITEM_SEPARATOR value)*
value: INT | FLOAT | STRING | IDENTIFIER | LSQBRACKET value_list? RSQBRACKET
constraint: "required" | "unique" | min_constraint | max_constraint | pattern_constraint | fk_constraint
min_constraint: "min" COLON INT
max_constraint: "max" COLON INT
pattern_constraint: "pattern" COLON STRING
fk_constraint: "foreign_key" COLON IDENTIFIER
relationship_definition: source_entity RELATIONSHIP_SYMBOL target_entity (LCURLYBRACE description RCURLYBRACE)?
source_entity: IDENTIFIER
target_entity: IDENTIFIER
description: STRING
api_definition: "api" COLON HTTP_METHOD STRING (LPAREN parameter_list? RPAREN)? (COLON type_definition)? (LCURLYBRACE description? RCURLYBRACE)?
ui_definition: "ui" COLON UI_COMPONENT (LPAREN parameter_list? RPAREN)? (navigation_flow)? (LCURLYBRACE description? RCURLYBRACE)?
navigation_flow: "->" LCURLYBRACE (event_target (ITEM_SEPARATOR event_target)*)? RCURLYBRACE
event_target: IDENTIFIER COLON IDENTIFIER (LPAREN parameter_list? RPAREN)?
```

## Implementation Details

### Parser

The parser uses the [Lark parsing library](https://github.com/lark-parser/lark) to convert DSL text into a parse tree:

```python
from pathlib import Path
from typing import Optional
from lark import Lark, Tree, Transformer

class DomainForgeParser:
    def __init__(self, grammar_file: Optional[str] = None, transformer: Optional[Transformer] = None) -> None:
        if grammar_file is None:
            current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
            grammar_file = str(current_dir / "grammar.lark")

        with open(grammar_file) as f:
            grammar = f.read()

        self.parser = Lark(grammar, start="start", parser="lalr")

        # Set the transformer
        self.transformer = transformer or IdentityTransformer()

    def parse(self, text: str) -> Tree:
        """Parse DSL text into a parse tree"""
        return self.parser.parse(text)

    def parse_file(self, file_path: str) -> Tree:
        """Parse a DSL file into a parse tree"""
        with open(file_path) as f:
            text = f.read()
        return self.parse(text)
```

### Transformer

The transformer converts parse trees into Pydantic models representing your domain:

```python
from lark import Transformer
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class DomainForgeTransformer(Transformer):
    def transform(self, tree: Tree) -> DomainModel:
        """Transform the parse tree into a domain model"""
        # Implementation details...
```

### Interpreter

The interpreter coordinates the parsing and transformation to generate code:

```python
class DomainForgeInterpreter:
    def __init__(self):
        self.parser = DomainForgeParser()
        self.transformer = DomainForgeTransformer()

    def interpret(self, text: str) -> DomainModel:
        """Parse and transform DSL text into a domain model"""
        parse_tree = self.parser.parse(text)
        return self.transformer.transform(parse_tree)

    def interpret_file(self, file_path: str) -> DomainModel:
        """Parse and transform a DSL file into a domain model"""
        with open(file_path, 'r') as f:
            text = f.read()
        return self.interpret(text)

    def generate_code(self, domain_model: DomainModel, output_dir: str) -> None:
        """Generate code from a domain model"""
        # Implementation details...
```

## Usage Instructions

### Installation

Install DomainForge using pip:

```bash
pip install domainforge
```

### Basic Usage

1. **Create a Domain Model File**:

```
// my-domain.domainforge
@Blog {
  #Post {
    id: UUID [required]
    title: String [required, minLength:3, maxLength:100]
    content: Text [required]
    published: Boolean = false
    publishedAt: DateTime?

    publish() {
      "Publish this post"
    }

    api: GET "/posts"
    api: GET "/posts/{id}"
    api: POST "/posts" (post: PostDTO): Post {
      "Create a new post"
    }

    ui: Form
  }

  #Comment {
    id: UUID [required]
    postId: UUID [required, foreign_key:Post]
    author: String [required]
    content: Text [required]
    createdAt: DateTime = "new Date()"

    api: GET "/posts/{postId}/comments"
    api: POST "/posts/{postId}/comments" (comment: CommentDTO): Comment
  }

  Post -> Comment
}
```

2. **Generate Your Application**:

```bash
domainforge generate my-domain.domainforge --output ./my-blog-app
```

3. **Run the Generated Applications**:

```bash
# Backend (FastAPI)
cd my-blog-app/backend
pip install -r requirements.txt
uvicorn src.main:app --reload

# Frontend (React)
cd my-blog-app/frontend
npm install
npm run dev
```

### Advanced Examples

#### Complex Domain Model

```
@ECommerce {
  #Product {
    id: UUID [required]
    name: String [required, minLength:3, maxLength:100]
    description: Text
    price: Decimal [required, min:0]
    inventory: Integer [required, min:0]
    categories: List<Category>
    attributes: Dict<String, String>
    images: List<String>

    reduceInventory(quantity: Integer) {
      "Reduce the inventory by the given quantity"
    }

    api: GET "/products" {
      "List all products"
    }
    api: GET "/products/{id}" {
      "Get product details"
    }

    ui: Detail (layout: "two-column")
    ui: Form
  }

  #Category {
    id: UUID [required]
    name: String [required, unique]
    description: Text
    parentId: UUID?

    api: GET "/categories"
    ui: Tree
  }

  #Order {
    id: UUID [required]
    customerId: UUID [required, foreign_key:Customer]
    items: List<OrderItem> [required]
    totalAmount: Decimal [required]
    status: String = "PENDING"
    createdAt: DateTime = "new Date()"

    completeOrder() {
      "Mark the order as complete"
    }

    cancelOrder() {
      "Cancel the order"
    }

    api: POST "/orders" (order: OrderDTO): Order
    api: GET "/orders/{id}"
    api: PUT "/orders/{id}/status" (status: String): Order

    ui: Detail (layout: "three-column")
  }

  %Address {
    street: String [required]
    city: String [required]
    state: String [required]
    zipCode: String [required, pattern:"\\d{5}"]
  }

  ^OrderPlaced {
    orderId: UUID [required]
    timestamp: DateTime = "new Date()"
  }

  >>OrderService {
    createOrder(customerId: UUID, items: List<OrderItem>): Order {
      "Create a new order"
    }

    api: POST "/orders/create" (orderData: OrderCreateDTO): Order
  }

  $ProductRepository {
    findByCategory(categoryId: UUID): List<Product> {
      "Find products by category"
    }
  }

  Product -> OrderItem
  Order -> OrderItem
  Customer <-> Order
  Product <-> Category
}
```

## Best Practices

1. **Organize by Bounded Context**: Group related entities, value objects, services, etc. within appropriate bounded contexts
2. **Follow DDD Principles**: Use entities for objects with identity, value objects for descriptive elements
3. **Be Explicit**: Use constraints and types to clearly express your domain model
4. **Consistent Naming**: Use consistent naming conventions (e.g., PascalCase for types, camelCase for properties)
5. **Single Responsibility**: Keep entities focused on a single responsibility
6. **Document**: Use descriptions to document the purpose of entities, methods, APIs, etc.

## Troubleshooting

| Problem | Possible Cause | Solution |
|---------|---------------|----------|
| Parser error | Syntax error in DSL file | Check for missing braces, incorrect symbols, etc. |
| Type not found | Using undefined type | Ensure all types are properly defined within your domain model |
| Generation error | Inconsistent relationships | Check that related entities exist and references are correct |
| UI component error | Invalid component parameters | Verify component parameters match expected types |

## API Reference

For detailed API documentation, see the [API Reference](api/index.md).

---

This documentation is continuously evolving. For the latest updates, please refer to the [official repository](https://github.com/yourusername/domain-forge).
