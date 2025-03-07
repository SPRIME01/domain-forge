import json
from json.decoder import JSONDecodeError

class JsonFileRepository:
    def __init__(self, filename: str) -> None:
        # ...existing code...
        self.filename = filename
        # ...existing code...

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
        # ...existing code...
        with open(self.filename, "w") as file:
            json.dump(data, file)
        # ...existing code...
