"""
Command-line interface for DomainForge.

This module provides the command-line interface for the DomainForge tool.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Optional, NoReturn

import click
from typing_extensions import Literal

from .core.interpreter import DomainForgeInterpreter
from .generators.python_backend_generator import PythonBackendGenerator
from .generators.typescript_frontend_generator import TypeScriptFrontendGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger: logging.Logger = logging.getLogger("domainforge")


@click.command()
@click.argument(
    "input_file", type=click.Path(exists=True, file_okay=True, dir_okay=False)
)
@click.option(
    "-o",
    "--output",
    "output_dir",
    type=click.Path(),
    default="./output",
    help="Output directory for generated code",
)
@click.option(
    "--backend-only",
    is_flag=True,
    help="Generate only the backend code",
)
@click.option(
    "--frontend-only",
    is_flag=True,
    help="Generate only the frontend code",
)
@click.option(
    "--export-model",
    is_flag=True,
    help="Export the domain model as JSON",
)
@click.option(
    "--model-path",
    type=click.Path(),
    help="Path where the domain model should be exported",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output",
)
def main(
    input_file: str,
    output_dir: str,
    backend_only: bool,
    frontend_only: bool,
    export_model: bool,
    model_path: Optional[str],
    verbose: bool,
) -> None:
    """
    DomainForge - Generate full-stack applications from domain models.

    INPUT_FILE: Path to the .domainforge DSL file
    """
    # Set log level
    if verbose:
        logger.setLevel(logging.DEBUG)

    logger.info(f"DomainForge v{get_version()}")
    logger.info(f"Processing input file: {input_file}")

    # Create output directory if it doesn't exist
    output_path: Path = Path(output_dir)
    if not output_path.exists():
        os.makedirs(output_path)
        logger.debug(f"Created output directory: {output_path}")

    try:
        # Parse and interpret the domain model
        interpreter: DomainForgeInterpreter = DomainForgeInterpreter()
        domain_model = interpreter.interpret_file(input_file)

        logger.info(
            f"Successfully interpreted domain model with "
            f"{len(domain_model.bounded_contexts)} bounded contexts"
        )

        # Export the domain model if requested
        if export_model:
            export_path: str = (
                model_path if model_path else str(output_path / "domain_model.json")
            )
            interpreter.export_model(domain_model, export_path)
            logger.info(f"Domain model exported to: {export_path}")

        # Generate backend code if requested
        if not frontend_only:
            logger.info("Generating Python backend code...")
            backend_dir: Path = output_path / "backend"
            os.makedirs(backend_dir, exist_ok=True)

            backend_generator: PythonBackendGenerator = PythonBackendGenerator(
                output_dir=str(backend_dir)
            )
            backend_generator.generate(domain_model)
            logger.info(f"Python backend code generated at: {backend_dir}")

        # Generate frontend code if requested
        if not backend_only:
            logger.info("Generating TypeScript frontend code...")
            frontend_dir: Path = output_path / "frontend"
            os.makedirs(frontend_dir, exist_ok=True)

            frontend_generator: TypeScriptFrontendGenerator = TypeScriptFrontendGenerator(
                output_dir=str(frontend_dir)
            )
            frontend_generator.generate(domain_model)
            logger.info(f"TypeScript frontend code generated at: {frontend_dir}")

        logger.info("Code generation completed successfully")

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        if verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


def get_version() -> str:
    """Get the current version of DomainForge."""
    try:
        from importlib.metadata import version

        return version("domainforge")
    except Exception:
        return "0.1.0"  # Default version if not installed


if __name__ == "__main__":
    main()  # type: ignore[no-untyped-call]
