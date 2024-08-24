import json
import os
from abc import ABC, abstractmethod
from dataclasses import asdict

from timekeeper.config import INDEX_FILENAME, projects_path
from timekeeper.entities import Project, Role, TimeEntry
from timekeeper.errors import ProjectNotFoundError


class ProjectIndex:
    def __init__(self):
        self.projects_path = projects_path()
        self.lookup_filename = INDEX_FILENAME
        self.lookup_file = f"{self.projects_path}/{self.lookup_filename}"

        if not os.path.exists(self.projects_path):
            os.makedirs(self.projects_path)

        if not os.path.exists(self.lookup_file):
            self._index_projects()

    def _load_index(self) -> dict:
        with open(self.lookup_file, "r") as f:
            return json.load(f)

    def _save_index(self, projects_dict: dict) -> None:
        with open(self.lookup_file, "w") as f:
            json.dump(projects_dict, f, indent=4)

    def _index_projects(self, projects_path: str = "") -> None:
        projects_path = projects_path or self.projects_path

        projects_dict: dict = {"projects": {}}
        files = os.listdir(projects_path)

        # check if the project file exists
        for file in files:
            if file not in [self.lookup_filename, ".DS_Store"]:
                projects_dict["projects"][file.split(".")[0]] = os.path.abspath(
                    f"{projects_path}/{file}"
                )

        self._save_index(projects_dict)

    def get_index(self) -> dict:
        return self._load_index()

    def update_index(self, project_path: str, project_name: str) -> None:
        projects_dict = self._load_index()
        projects_dict["projects"][project_name] = f"{project_path}/{project_name}.json"
        self._save_index(projects_dict)

    def list_vaults(self) -> list:
        return list(
            set(
                [
                    os.path.dirname(file_path)
                    for file_path in self._load_index()["projects"].values()
                ]
            )
        )

    def list_projects(self) -> list:
        return list(self._load_index()["projects"].keys())

    def exists(self, project_name: str) -> bool:
        return project_name in self.list_projects()

    def get_project_vault_path(self, project_name: str) -> str:
        try:
            project_filepath = self._load_index()["projects"][project_name]
            # return the directory "vault" of the project file
            return str(os.path.dirname(project_filepath))
        except KeyError:
            raise ProjectNotFoundError(project_name)


class ProjectStorage(ABC):
    """Abstract class for a project repository backend"""

    @abstractmethod
    def use_vault(self, vault: str) -> None:
        """Set the vault to use"""

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
        os.makedirs(base_path, exist_ok=True)
        self.base_path = base_path

    def use_vault(self, vault_path: str) -> None:
        self.base_path = vault_path

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
