from dataclasses import dataclass, asdict
from typing import List
import os

VALID_KINDS = {"command", "application", "script", "project"}

@dataclass
class Entry:
    name: str
    kind: str
    executable: str
    arguments: List[str]
    working_dir: str = ""
    favorite: bool = False
    id: int = None

    def validate(self):
        if not self.name.strip() or self.kind not in VALID_KINDS:
            raise ValueError("Invalid name or entry type")
        if not self.executable.strip():
            raise ValueError("Executable or path is required")
        if self.working_dir and not os.path.isdir(self.working_dir):
            raise ValueError("Working directory does not exist")
        if self.kind == "project" and not os.path.isdir(os.path.expanduser(self.executable)):
            raise ValueError("Project folder does not exist")

    def to_dict(self):
        data = asdict(self)
        data.pop("id", None)
        return data
