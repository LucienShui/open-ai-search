import os
import pathlib
from typing import TextIO, Optional


class ProjectRoot:
    def __init__(self):
        self.target = "pyproject.toml"
        self.project_root = pathlib.Path(__file__).parent
        while self.target not in os.listdir(str(self.project_root)):
            self.project_root = self.project_root.parent

    def path(self, path: Optional[str] = None) -> str:
        return os.path.join(self.project_root, path or "")

    def open(self, path: str, *args, **kwargs) -> TextIO:
        return open(self.path(path), *args, **kwargs)


project_root = ProjectRoot()

__all__ = ["project_root"]
