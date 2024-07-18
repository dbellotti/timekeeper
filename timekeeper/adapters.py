import json
import os
from abc import ABC, abstractmethod
from dataclasses import asdict

from timekeeper.entities import Project, Role, TimeEntry
from timekeeper.errors import ProjectNotFoundError


class ProjectStorage(ABC):
    """Abstract class for a project repository backend"""

    @abstractmethod
    def load(self, project_name: str) -> Project:
        """Load a project by name"""

    @abstractmethod
    def save(self, project) -> None:
        """Save a project"""

    @abstractmethod
    def exists(self, project_name: str) -> bool:
        """Check if a project exists"""


class ProjectFileStorage(ProjectStorage):
    def __init__(self, base_path):
        if not os.path.exists(base_path):
            os.makedirs(base_path)
        self.base_path = base_path

    def path(self, project_name: str) -> str:
        return f"{self.base_path}/{project_name}.json"

    def load(self, project_name: str) -> Project:
        if self.exists(project_name):
            with open(self.path(project_name), "r") as f:
                project_dict = json.load(f)
            return self._load_objects(project_dict)
        else:
            raise ProjectNotFoundError(project_name)

    def save(self, project: Project) -> None:
        project_path = self.path(project.name)
        file_path = os.path.join(os.getcwd(), project_path)

        with open(file_path, "w") as f:
            json.dump(asdict(project), f, indent=4)

    def exists(self, project_name: str) -> bool:
        return os.path.exists(self.path(project_name))

    def _load_objects(self, project_dict: dict) -> Project:
        project = Project(**project_dict)
        project.roles = [Role(**role_dict) for role_dict in project_dict["roles"]]
        project.time_entries = [
            TimeEntry(**te_dict) for te_dict in project_dict["time_entries"]
        ]
        return project
