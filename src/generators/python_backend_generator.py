"""
Python backend code generator.

This module generates Python backend code from domain models using FastAPI and SQLAlchemy.
"""

import logging
from pathlib import Path
from typing import Dict, Any

from .base_generator import BaseGenerator
from ..core.models import BoundedContext, Entity, Service, ValueObject, DomainModel

logger = logging.getLogger(__name__)


class PythonBackendGenerator(BaseGenerator):
    """Generator for Python backend code using FastAPI and SQLAlchemy."""

    def __init__(self, output_dir: str):
        """Initialize the Python backend generator."""
        super().__init__(output_dir, template_dir=str(Path(__file__).parent.parent / "templates" / "python"))

        # Create standard directories
        self.src_dir = self.output_dir / "src"
        self.tests_dir = self.output_dir / "tests"

        for directory in [self.src_dir, self.tests_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    def generate_context(self, context: BoundedContext) -> None:
        """
        Generate code for a bounded context.

        Args:
            context: The bounded context to generate code for
        """
        logger.info(f"Generating Python code for bounded context: {context.name}")

        # Create context directory structure
        context_dir = self.src_dir / context.name.lower()
        context_dir.mkdir(exist_ok=True)

        # Create layer directories
        domain_dir = context_dir / "domain"
        application_dir = context_dir / "application"
        infrastructure_dir = context_dir / "infrastructure"
        api_dir = context_dir / "api"

        for directory in [domain_dir, application_dir, infrastructure_dir, api_dir]:
            directory.mkdir(exist_ok=True)
            (directory / "__init__.py").touch()

        # Generate code for each component
        self._generate_domain_layer(context, domain_dir)
        self._generate_application_layer(context, application_dir)
        self._generate_infrastructure_layer(context, infrastructure_dir)
        self._generate_api_layer(context, api_dir)

        # Generate tests
        self._generate_tests(context)

    def _generate_domain_layer(self, context: BoundedContext, output_dir: Path) -> None:
        """Generate domain layer code."""
        logger.debug(f"Generating domain layer for {context.name}")

        # Create subdirectories
        entities_dir = output_dir / "entities"
        repositories_dir = output_dir / "repositories"
        value_objects_dir = output_dir / "value_objects"
        services_dir = output_dir / "services"

        for directory in [entities_dir, repositories_dir, value_objects_dir, services_dir]:
            directory.mkdir(exist_ok=True)
            (directory / "__init__.py").touch()

        # Generate entities
        for entity in context.entities:
            # Entity class
            self.render_template(
                "domain/entity.py.j2",
                {"context": context, "entity": entity},
                entities_dir / f"{entity.name.lower()}.py"
            )

            # Repository interface
            if entity.repository:
                self.render_template(
                    "domain/repository.py.j2",
                    {"context": context, "entity": entity},
                    repositories_dir / f"{entity.name.lower()}_repository.py"
                )

        # Generate value objects
        for vo in context.value_objects:
            self.render_template(
                "domain/value_object.py.j2",
                {"context": context, "value_object": vo},
                value_objects_dir / f"{vo.name.lower()}.py"
            )

        # Generate domain services
        for service in context.services:
            self.render_template(
                "domain/service.py.j2",
                {"context": context, "service": service},
                services_dir / f"{service.name.lower()}.py"
            )

    def _generate_application_layer(self, context: BoundedContext, output_dir: Path) -> None:
        """Generate application layer code."""
        logger.debug(f"Generating application layer for {context.name}")

        # Create subdirectories
        dtos_dir = output_dir / "dtos"
        use_cases_dir = output_dir / "use_cases"

        for directory in [dtos_dir, use_cases_dir]:
            directory.mkdir(exist_ok=True)
            (directory / "__init__.py").touch()

        # Generate DTOs and use cases for each entity
        for entity in context.entities:
            # DTOs
            self.render_template(
                "application/dto.py.j2",
                {"context": context, "entity": entity},
                dtos_dir / f"{entity.name.lower()}_dto.py"
            )

            # Use cases
            self.render_template(
                "application/use_case.py.j2",
                {"context": context, "entity": entity},
                use_cases_dir / f"{entity.name.lower()}_use_case.py"
            )

    def _generate_infrastructure_layer(self, context: BoundedContext, output_dir: Path) -> None:
        """Generate infrastructure layer code."""
        logger.debug(f"Generating infrastructure layer for {context.name}")

        # Create subdirectories
        persistence_dir = output_dir / "persistence"
        persistence_dir.mkdir(exist_ok=True)
        (persistence_dir / "__init__.py").touch()

        # Generate SQLAlchemy models
        self.render_template(
            "infrastructure/models.py.j2",
            {"context": context},
            persistence_dir / "models.py"
        )

        # Generate repository implementations
        for entity in context.entities:
            if entity.repository:
                self.render_template(
                    "infrastructure/repository.py.j2",
                    {"context": context, "entity": entity},
                    persistence_dir / f"{entity.name.lower()}_repository.py"
                )

    def _generate_api_layer(self, context: BoundedContext, output_dir: Path) -> None:
        """Generate API layer code."""
        logger.debug(f"Generating API layer for {context.name}")

        # Create controllers directory
        controllers_dir = output_dir / "controllers"
        controllers_dir.mkdir(exist_ok=True)
        (controllers_dir / "__init__.py").touch()

        # Generate controllers for each entity
        for entity in context.entities:
            if entity.apis:
                self.render_template(
                    "api/controller.py.j2",
                    {"context": context, "entity": entity},
                    controllers_dir / f"{entity.name.lower()}_controller.py"
                )

    def _generate_tests(self, context: BoundedContext) -> None:
        """Generate tests for all components."""
        logger.debug(f"Generating tests for {context.name}")

        # Create test directories
        context_test_dir = self.tests_dir / context.name.lower()
        domain_test_dir = context_test_dir / "domain"
        application_test_dir = context_test_dir / "application"
        infrastructure_test_dir = context_test_dir / "infrastructure"
        api_test_dir = context_test_dir / "api"

        for directory in [context_test_dir, domain_test_dir, application_test_dir,
                         infrastructure_test_dir, api_test_dir]:
            directory.mkdir(parents=True, exist_ok=True)
            (directory / "__init__.py").touch()

        # TODO: Generate actual test files
