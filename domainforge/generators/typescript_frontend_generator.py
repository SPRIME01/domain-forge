"""TypeScript frontend code generator.

This module generates TypeScript/React frontend code from domain models.
"""

import logging
from pathlib import Path

from ..core.models import BoundedContext, DomainModel
from .base_generator import BaseGenerator

logger = logging.getLogger(__name__)


class TypeScriptFrontendGenerator(BaseGenerator):
    """Generator for TypeScript/React frontend code."""

    def __init__(self, output_dir: str):
        """Initialize the TypeScript frontend generator."""
        # Find the project root directory to locate the templates correctly
        project_root = Path(__file__).parent.parent.parent
        template_dirs = [
            str(Path(__file__).parent.parent / "templates" / "typescript"),
            str(project_root / "templates" / "typescript"),
        ]

        # Use the first template directory that exists
        template_dir = next(
            (dir_path for dir_path in template_dirs if Path(dir_path).exists()), None
        )

        super().__init__(
            output_dir,
            template_dir=template_dir,
        )

        # Create standard directories
        self.src_dir = self.output_dir / "src"
        self.src_dir.mkdir(parents=True, exist_ok=True)

        # Store domain model for template rendering
        self.model = None

    def generate(self, model: DomainModel) -> None:
        """Generate code from a domain model.

        Args:
        ----
            model: The domain model to generate code from. Contains all bounded contexts,
                  entities, and their relationships that will be used to generate the
                  TypeScript/React frontend application structure.

        """
        # Store the model for template rendering
        self.model = model

        super().generate(model)

        # Generate shared/common code
        self._generate_common_files()

        # Copy necessary config files
        self._copy_config_files()

    def generate_context(self, context: BoundedContext) -> None:
        """Generate code for a bounded context.

        Args:
        ----
            context: The bounded context to generate code for. Contains the entities,
                    value objects, and relationships that will be used to generate
                    the TypeScript implementation of this specific domain context.

        """
        logger.info(f"Generating TypeScript code for bounded context: {context.name}")

        # Create context directory structure
        context_dir = self.src_dir / context.name.lower()
        context_dir.mkdir(exist_ok=True)

        # Create layer directories
        domain_dir = context_dir / "domain"
        application_dir = context_dir / "application"
        infrastructure_dir = context_dir / "infrastructure"
        ui_dir = context_dir / "ui"

        for directory in [domain_dir, application_dir, infrastructure_dir, ui_dir]:
            directory.mkdir(exist_ok=True)

        # Generate code for each component
        self._generate_domain_layer(context, domain_dir)
        self._generate_application_layer(context, application_dir)
        self._generate_infrastructure_layer(context, infrastructure_dir)
        self._generate_ui_layer(context, ui_dir)

    def _generate_domain_layer(self, context: BoundedContext, output_dir: Path) -> None:
        """Generate domain layer code."""
        logger.debug(f"Generating domain layer for {context.name}")

        # Create subdirectories
        entities_dir = output_dir / "entities"
        value_objects_dir = output_dir / "value-objects"
        services_dir = output_dir / "services"

        for directory in [entities_dir, value_objects_dir, services_dir]:
            directory.mkdir(exist_ok=True)

        # Generate entities
        for entity in context.entities:
            self.render_template(
                "domain/entity.ts.j2",
                {"context": context, "entity": entity},
                entities_dir / f"{entity.name.lower()}.ts",
            )

        # Generate value objects
        for vo in context.value_objects:
            self.render_template(
                "domain/value-object.ts.j2",
                {"context": context, "value_object": vo},
                value_objects_dir / f"{vo.name.lower()}.ts",
            )

    def _generate_application_layer(
        self, context: BoundedContext, output_dir: Path
    ) -> None:
        """Generate application layer code."""
        logger.debug(f"Generating application layer for {context.name}")

        # Create subdirectories
        dtos_dir = output_dir / "dtos"
        use_cases_dir = output_dir / "use-cases"
        mappers_dir = output_dir / "mappers"

        for directory in [dtos_dir, use_cases_dir, mappers_dir]:
            directory.mkdir(exist_ok=True)

        # Generate DTOs, use cases, and mappers for each entity
        for entity in context.entities:
            # DTOs
            self.render_template(
                "application/dto.ts.j2",
                {"context": context, "entity": entity},
                dtos_dir / f"{entity.name.lower()}-dto.ts",
            )

            # Use cases
            self.render_template(
                "application/use-case.ts.j2",
                {"context": context, "entity": entity},
                use_cases_dir / f"{entity.name.lower()}-use-case.ts",
            )

            # Mappers
            self.render_template(
                "application/mapper.ts.j2",
                {"context": context, "entity": entity},
                mappers_dir / f"{entity.name.lower()}-mapper.ts",
            )

    def _generate_infrastructure_layer(
        self, context: BoundedContext, output_dir: Path
    ) -> None:
        """Generate infrastructure layer code."""
        logger.debug(f"Generating infrastructure layer for {context.name}")

        # Create subdirectories
        api_dir = output_dir / "api"
        store_dir = output_dir / "store"

        for directory in [api_dir, store_dir]:
            directory.mkdir(exist_ok=True)

        # Generate API clients and stores for each entity
        for entity in context.entities:
            if entity.apis:
                # API client
                self.render_template(
                    "infrastructure/api-client.ts.j2",
                    {"context": context, "entity": entity},
                    api_dir / f"{entity.name.lower()}-api-client.ts",
                )

            # MobX store
            self.render_template(
                "infrastructure/store.ts.j2",
                {"context": context, "entity": entity},
                store_dir / f"{entity.name.lower()}-store.ts",
            )

    def _generate_ui_layer(self, context: BoundedContext, output_dir: Path) -> None:
        """Generate UI layer code."""
        logger.debug(f"Generating UI layer for {context.name}")

        # Create subdirectories
        components_dir = output_dir / "components"
        pages_dir = output_dir / "pages"
        hooks_dir = output_dir / "hooks"

        for directory in [components_dir, pages_dir, hooks_dir]:
            directory.mkdir(exist_ok=True)

        # Generate components and pages for each entity
        for entity in context.entities:
            # Components
            for ui in entity.uis:
                if ui.component_type == "Form":
                    self.render_template(
                        "ui/components/form.tsx.j2",
                        {"context": context, "entity": entity},
                        components_dir / f"{entity.name.lower()}-form.tsx",
                    )
                elif ui.component_type == "Table":
                    self.render_template(
                        "ui/components/table.tsx.j2",
                        {"context": context, "entity": entity},
                        components_dir / f"{entity.name.lower()}-table.tsx",
                    )

            # Pages
            self.render_template(
                "ui/pages/list-page.tsx.j2",
                {"context": context, "entity": entity},
                pages_dir / f"{entity.name.lower()}-list.tsx",
            )
            self.render_template(
                "ui/pages/detail-page.tsx.j2",
                {"context": context, "entity": entity},
                pages_dir / f"{entity.name.lower()}-detail.tsx",
            )
            self.render_template(
                "ui/pages/edit-page.tsx.j2",
                {"context": context, "entity": entity},
                pages_dir / f"{entity.name.lower()}-edit.tsx",
            )

    def _generate_common_files(self) -> None:
        """Generate common files for the frontend application."""
        if not self.model:
            raise ValueError("Domain model not set. Call generate() first.")

        # Generate main app files
        self.render_template(
            "app/App.tsx.j2", {"model": self.model}, self.src_dir / "App.tsx"
        )
        self.render_template(
            "app/main.tsx.j2", {"model": self.model}, self.src_dir / "main.tsx"
        )
        self.render_template(
            "app/vite-env.d.ts.j2",
            {"model": self.model},
            self.src_dir / "vite-env.d.ts",
        )

        # Generate common utilities
        utils_dir = self.src_dir / "utils"
        utils_dir.mkdir(exist_ok=True)
        self.render_template(
            "utils/http-client.ts.j2",
            {"model": self.model},
            utils_dir / "http-client.ts",
        )

    def _copy_config_files(self) -> None:
        """Copy configuration files for the frontend application."""
        config_files = {
            "package.json": {
                "name": "frontend",
                "private": True,
                "version": "0.0.0",
                "type": "module",
                "scripts": {
                    "dev": "vite",
                    "build": "tsc && vite build",
                    "preview": "vite preview",
                },
                "dependencies": {
                    "react": "^18.2.0",
                    "react-dom": "^18.2.0",
                    "react-router-dom": "^6.4.0",
                    "mobx": "^6.6.0",
                    "mobx-react-lite": "^3.4.0",
                    "axios": "^1.6.0",
                    "@mantine/core": "^7.0.0",
                    "@mantine/hooks": "^7.0.0",
                    "@mantine/form": "^7.0.0",
                },
                "devDependencies": {
                    "@types/react": "^18.2.0",
                    "@types/react-dom": "^18.2.0",
                    "@vitejs/plugin-react": "^4.2.0",
                    "typescript": "^5.0.0",
                    "vite": "^5.0.0",
                },
            },
            "tsconfig.json": {
                "compilerOptions": {
                    "target": "ES2020",
                    "useDefineForClassFields": True,
                    "lib": ["ES2020", "DOM", "DOM.Iterable"],
                    "module": "ESNext",
                    "skipLibCheck": True,
                    "moduleResolution": "bundler",
                    "allowImportingTsExtensions": True,
                    "resolveJsonModule": True,
                    "isolatedModules": True,
                    "noEmit": True,
                    "jsx": "react-jsx",
                    "strict": True,
                    "noUnusedLocals": True,
                    "noUnusedParameters": True,
                    "noFallthroughCasesInSwitch": True,
                },
                "include": ["src"],
                "references": [{"path": "./tsconfig.node.json"}],
            },
            "vite.config.ts": """
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
})
""",
        }

        for filename, content in config_files.items():
            file_path = self.output_dir / filename
            if isinstance(content, dict):
                import json

                json_content = json.dumps(content, indent=2)
                with open(file_path, "w") as f:
                    f.write(json_content)
            else:
                with open(file_path, "w") as f:
                    f.write(str(content))
