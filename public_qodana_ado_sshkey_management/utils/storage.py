import json
from pathlib import Path
from typing import List
from dataclasses import asdict
from ..models.projects_info import ProjectInfo

DATA_FILE = Path("data/projects_info.json")

def load_projects_info() -> List[ProjectInfo]:
    if DATA_FILE.exists():
        try:
            with DATA_FILE.open() as f:
                content = f.read().strip()
                if not content:
                    return []
                return [ProjectInfo(**d) for d in json.loads(content)]
        except json.JSONDecodeError:
            print("⚠️ Warning: Invalid or empty JSON file, resetting projects_info.json")
            return []
    return []

def save_projects_info(data: List[ProjectInfo]):
    with DATA_FILE.open("w") as f:
        json.dump([asdict(d) for d in data], f, indent=2)
