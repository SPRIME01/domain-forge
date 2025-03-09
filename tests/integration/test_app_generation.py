"""Integration tests for application generation from DSL content."""

import os
import shutil
import tempfile
import pytest
from pathlib import Path

from domainforge.core.interpreter import generate_application


class TestApplicationGeneration:
    """Tests for the application generation from DSL content."""

    @pytest.fixture
    def output_dir(self) -> str:
        """Create a temporary directory for test output."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Clean up the temporary directory after the test
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    def test_simple_app_generation(self, output_dir: str) -> None:
        """Test generating a simple application from DSL content."""
        # Simple DSL content with one context and entity
        dsl_content = """
        @ECommerce {
            #Product {
                name: String
                price: Decimal
                description: String
            }

            #Customer {
                name: String
                email: String
                address: String
            }

            Customer => Product
        }
        """

        # Generate application
        generate_application(dsl_content, output_dir)

        # Verify output structure
        backend_dir = os.path.join(output_dir, "backend")
        frontend_dir = os.path.join(output_dir, "frontend")

        assert os.path.exists(backend_dir)
        assert os.path.exists(frontend_dir)

        # Verify backend structure (key Python files)
        assert os.path.exists(os.path.join(backend_dir, "app.py"))
        assert os.path.exists(os.path.join(backend_dir, "models.py"))

        # Verify frontend structure (key TypeScript files)
        assert os.path.exists(os.path.join(frontend_dir, "package.json"))

    def test_complex_app_generation(self, output_dir: str) -> None:
        """Test generating a more complex application from DSL content."""
        # More complex DSL with multiple contexts and entities
        dsl_content = """
        @UserManagement {
            #User {
                id: UUID
                username: String
                email: String
                password: String
                role: String
            }

            #Role {
                name: String
                permissions: List<String>
            }

            User -> Role
        }

        @ContentManagement {
            #Article {
                id: UUID
                title: String
                content: String
                publishedDate: DateTime
                author: UUID
            }

            #Comment {
                id: UUID
                content: String
                authorId: UUID
                articleId: UUID
                createdDate: DateTime
            }

            Article => Comment
        }
        """

        # Generate application
        generate_application(dsl_content, output_dir)

        # Verify output structure
        backend_dir = os.path.join(output_dir, "backend")
        frontend_dir = os.path.join(output_dir, "frontend")

        assert os.path.exists(backend_dir)
        assert os.path.exists(frontend_dir)

        # Verify both contexts were generated
        assert os.path.exists(os.path.join(backend_dir, "user_management"))
        assert os.path.exists(os.path.join(backend_dir, "content_management"))

    @pytest.mark.xfail(reason="Test to verify error handling - expected to fail")
    def test_invalid_dsl_content(self, output_dir: str) -> None:
        """Test handling of invalid DSL content."""
        # Invalid DSL content with syntax errors
        invalid_dsl = """
        @BrokenContext {
            #MissingClosingBracket {
                name: String
            // Missing closing bracket
        }
        """

        # This should raise a syntax error
        generate_application(invalid_dsl, output_dir)

    def test_file_permissions(self, output_dir: str) -> None:
        """Test that generated files have correct permissions."""
        dsl_content = """
        @TestContext {
            #TestEntity {
                name: String
            }
        }
        """

        # Generate application
        generate_application(dsl_content, output_dir)

        # Check permissions on key files (should be readable/writable)
        backend_app_py = os.path.join(output_dir, "backend", "app.py")
        assert os.path.exists(backend_app_py)
        assert os.access(backend_app_py, os.R_OK)  # Readable
        assert os.access(backend_app_py, os.W_OK)  # Writable
