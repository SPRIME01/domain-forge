"""
Utility script to clean up Python cache files.
Run this script to resolve import conflicts between modules with the same name.
"""

import os
import pathlib
import shutil
import sys


def clean_cache_files(base_path=None):
    """
    Clean all __pycache__ directories and .pyc files from the project.

    Args:
        base_path: Base directory to start cleaning from. Defaults to current directory.
    """
    if base_path is None:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    base_path = pathlib.Path(base_path)
    print(f"Cleaning Python cache files from: {base_path}")

    # Remove .pyc files
    pyc_count = 0
    for pyc_file in base_path.rglob("*.pyc"):
        print(f"Removing: {pyc_file}")
        pyc_file.unlink()
        pyc_count += 1

    # Remove __pycache__ directories
    pycache_count = 0
    for pycache_dir in base_path.rglob("__pycache__"):
        if pycache_dir.is_dir():
            print(f"Removing directory: {pycache_dir}")
            shutil.rmtree(pycache_dir)
            pycache_count += 1

    print(
        f"Cleanup complete. Removed {pyc_count} .pyc files and {pycache_count} __pycache__ directories."
    )


if __name__ == "__main__":
    # Allow specifying a custom base path
    base_path = sys.argv[1] if len(sys.argv) > 1 else None
    clean_cache_files(base_path)
    print("Python cache cleanup completed successfully!")
