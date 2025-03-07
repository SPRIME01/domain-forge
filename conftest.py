"""
Pytest configuration file.

Ensures the repository root is added to sys.path and provides common fixtures.
"""

import sys
from pathlib import Path

# Compute the repository root (where domainforge package resides)
repo_root: Path = Path(__file__).resolve().parent

# Insert repo_root into sys.path if not already present
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

# Configure pytest-asyncio to use session scope by default
def pytest_configure(config):
    """Configure pytest-asyncio to use session scope."""
    config.option.asyncio_mode = "strict"
    config.option.asyncio_default_fixture_loop_scope = "session"

