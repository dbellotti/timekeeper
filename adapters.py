import json
import os
from dataclasses import asdict

from entities import Project, Role, TimeEntry
from errors import ProjectNotFoundError


class ProjectFileRepository:
    def __init__(self, base_path):
        if not os.path.exists(base_path):
            os.makedirs(base_path)
        self.base_path = base_path

    def path(self, project_name):
        return f"{self.base_path}/{project_name}.json"

    def load(self, project_name) -> Project:
        project_path = self.path(project_name)

        if os.path.exists(project_path):
            with open(project_path, "r") as f:
                project_dict = json.load(f)
            return self._load_objects(project_dict)
        else:
            raise ProjectNotFoundError(project_name)

    def save(self, project):
        project_path = self.path(project.name)
        file_path = os.path.join(os.getcwd(), project_path)

        with open(file_path, "w") as f:
            json.dump(asdict(project), f, indent=4)

    def _load_objects(self, project_dict: dict) -> Project:
        project = Project(**project_dict)
        project.roles = [Role(**role_dict) for role_dict in project_dict["roles"]]
        project.time_entries = [
            TimeEntry(**te_dict) for te_dict in project_dict["time_entries"]
        ]
        return project
