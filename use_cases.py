import os
from datetime import datetime

from adapters import ProjectFileRepository
from entities import Project, Role, TimeEntry


class UserQuitException(Exception):
    """Exception raised when an invalid time is provided."""


class InitializeProjectWizard:
    def __init__(self, project_repo: ProjectFileRepository):
        self.project_repo = project_repo

    def execute(self):
        print()
        project_name = input("Enter project name: ")
        project = self._find_or_create_project(project_name)
        project_path = self.project_repo.path(project_name)
        print(f'\n\tProject "{project}" created at "{project_path}".\n')

        role_name = input("Enter a project role: ")
        self._find_or_get_role_name(project, role_name)
        hourly_rate = input("Enter a hourly rate for this role: ")
        if hourly_rate == "":
            hourly_rate = 0
        project.add_role(Role(name=role_name, hourly_rate=int(hourly_rate)))

        # TODO
        # not sure the format to save the project, currently just dumping the project
        # dict we'll need to make sure saving and retrieving time entries
        # (for ToggleTrackingInteractor) matches the format in the older version
        # of time_tracking.json
        self.project_repo.save(project)
        print(f'\n\tRole "{role_name}" added with rate of ${hourly_rate}/hour.\n')
        return project

    def _find_or_create_project(self, project_name) -> Project:
        if os.path.exists(self.project_repo.path(project_name)):
            print(f"Project {project_name} already exists.")
            action = input(
                "Do you want to add a new role/rate or quit? Enter 'role' to add a role or 'quit' to exit: "
            ).lower()
            if action == "quit":
                raise UserQuitException("...project creation abandoned, goodbye")
            return self.project_repo.load(project_name)
        return Project(name=project_name)

    def _find_or_get_role_name(self, project, role_name):
        while any(role_name == role["name"] for role in project.roles):
            print(f"Role {role_name} already exists.")
            role_name = input(
                "Enter a different name for the role or type 'quit' to exit: "
            )
            if role_name.lower() == "quit":
                raise UserQuitException("...project creation abandoned, goodbye")
            else:
                return role_name


class ToggleTrackingInteractor:
    def __init__(self, project_repo):
        self.project_repo = project_repo

    def execute(self, project_name):
        project = self.project_repo.load(project_name)

        if project.last_time_entry_is_open():
            return StopTracking(project).execute()
        else:
            return StartTracking(project).execute()


class TrackTime:
    def __init__(self, project_repo: ProjectFileRepository):
        self.project_repo = project_repo

    def execute(self, project_name: str):
        project = self.project_repo.load(project_name)
        self._make_time_entry(project)
        self.project_repo.save(project)

    def _make_time_entry(self, project) -> None:
        raise NotImplementedError

    def _default_role(self, project):
        # assuming the first role is the default role
        return project.roles[0]

    def _get_datetime(self):
        return datetime.now()


class StartTracking(TrackTime):
    def _make_time_entry(self, project) -> None:
        time_entry = TimeEntry(
            self._default_role(project).name, str(self._get_datetime()), None
        )
        project.add_time_entry(time_entry)
        print(f"Started tracking for {project} at {time_entry.start_time}.")


class StopTracking(TrackTime):
    def _make_time_entry(self, project) -> None:
        time_entry = project.time_entries[-1]
        time_entry.end_time = str(self._get_datetime())
        print(f"Stopped tracking for {project} at {time_entry.start_time}.")


class SummarizeTime:
    # Implementation details to calculate and summarize time.
    pass
