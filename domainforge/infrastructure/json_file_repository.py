"""JSON file-based repository implementation.

This module provides a simple JSON file-based repository implementation for
storing and retrieving data in a local JSON file.
"""

import json
from json.decoder import JSONDecodeError


class JsonFileRepository:
    """Repository implementation that stores data in a JSON file.

    This class provides basic CRUD operations for storing and retrieving
    data using a JSON file as the persistence mechanism. Useful for
    simple storage needs or testing purposes.
    """

    def __init__(self, filename: str) -> None:
        """Initialize the JSON file repository.

        Args:
        ----
            filename: Path to the JSON file that will store the repository data.
                    Will be created if it doesn't exist.

        """
        self.filename = filename

    def _read_file(self) -> dict:
        try:
            with open(self.filename, "r") as file:
                content = file.read().strip()
                if not content:
                    return {}  # File empty – return empty repository state
                return json.loads(content)
        except JSONDecodeError:
            return {}  # Malformed JSON – default to empty state

    def _write_file(self, data: dict) -> None:
        with open(self.filename, "w") as file:
            json.dump(data, file)
