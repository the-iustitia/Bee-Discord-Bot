import json
from pathlib import Path

def load(path):
    path = Path(path)

    if not path.exists():
        path.write_text("{}", encoding="utf-8")
        return {}

    try:
        data = path.read_text(encoding="utf-8").strip()

        if not data:
            path.write_text("{}", encoding="utf-8")
            return {}

        return json.loads(data)

    except json.JSONDecodeError:
        backup = path.with_suffix(".corrupt.json")
        path.replace(backup)

        path.write_text("{}", encoding="utf-8")
        return {}