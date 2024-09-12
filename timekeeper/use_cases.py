from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Type

from timekeeper.adapters import ProjectIndex, ProjectStorage
from timekeeper.config import projects_path
from timekeeper.entities import Project, Role
from timekeeper.errors import (
    PreviousTimeEntryClosedException,
    PreviousTimeEntryOpenException,
    RoleNotFoundError,
    UserQuitException,
)


class InitializeVaultWizard:
    def __init__(self, project_storage_class: Type[ProjectStorage]) -> None:
        self.project_storage_class = project_storage_class

    def execute(self) -> ProjectStorage:
        default_path = projects_path()
        project_path = (
            input(
                f"Where would you like your project to be stored? Press Enter to use {default_path}: ",
            )
            or default_path
        )
        return self.project_storage_class(project_path)


class InitializeProjectWizard:
    def __init__(self, project_storage: ProjectStorage):
        self.project_storage = project_storage
        self.project_lookup = ProjectIndex()

    def execute(self) -> Project:
        print()
        project_name = input("Enter project name: ")
        project = self._find_or_create_project(project_name)

        role_name = input("Enter a project role: ")
        self._find_or_get_role_name(project, role_name)
        hourly_rate_input = input("Enter a hourly rate for this role: ")
        try:
            hourly_rate = int(hourly_rate_input or 0)
        except ValueError:
            hourly_rate = 0
        project.add_role(Role(name=role_name, hourly_rate=hourly_rate))
        print(f'\n\tRole "{role_name}" added with rate of ${hourly_rate}/hour.\n')

        return self._save_project(project)

    def _save_project(self, project) -> Project:
        self.project_storage.save(project)
        print(f'\n\tProject "{project.name}" saved.\n')
        return project

    def _find_or_create_project(self, project_name) -> Project:
        if self.project_lookup.exists(project_name):
            print(f"Project {project_name} already exists.")
            action = input(
                "Do you want to add a new role/rate or quit? Enter 'role' to add a role or 'quit' to exit: "
            ).lower()
            if action == "quit":
                raise UserQuitException
            # Find the path the correct vault before trying to load the project
            vault_path = self.project_lookup.get_project_vault_path(project_name)
            self.project_storage.use_vault(vault_path)
            return self.project_storage.load(project_name)

        project = Project(name=project_name)
        print(f'\n\tProject "{project_name}" initialized.\n')
        return project

    def _find_or_get_role_name(self, project, role_name):
        while project.has_role(role_name):
            print(f"Role {role_name} already exists.")
            role_name = input(
                "Enter a different name for the role or type 'quit' to exit: "
            )
            if role_name.lower() == "quit":
                raise UserQuitException
            else:
                return role_name


class ToggleTrackingInteractor:
    def execute(self, project: Project, role_name: str) -> None:
        try:
            role = project.get_role(role_name)
        except RoleNotFoundError:
            print(f"Role {role_name} not found in project {project.name}.")
            role = project.get_default_role()
            print(f"Defaulted to role '{role.name}'.")

        if project.last_time_entry(role.name).is_open():
            StopTracking.execute(project, role)
        else:
            StartTracking.execute(project, role)


class StartTracking:
    @staticmethod
    def execute(project: Project, role: Role) -> None:
        StartTracking.raise_errors(project, role.name)
        project.start_time_entry(role.name)
        print(f"Started tracking at {project.last_time_entry().start_time}")

    @staticmethod
    def raise_errors(project: Project, role_name: str) -> None:
        if project.last_time_entry(role_name).is_open():
            raise PreviousTimeEntryOpenException


class StopTracking:
    @staticmethod
    def execute(project: Project, role: Role) -> None:
        StopTracking.raise_errors(project, role.name)
        project.end_time_entry(role.name)
        print(f"Stopped tracking at {project.last_time_entry().end_time}")

    @staticmethod
    def raise_errors(project: Project, role_name: str) -> None:
        if project.last_time_entry(role_name).is_closed():
            raise PreviousTimeEntryClosedException


class SummarizeTime:
    def execute(self, period: str, project: Project, precise=False) -> None:
        period_summary: defaultdict = defaultdict(lambda: defaultdict(timedelta))

        for time_entry in project.time_entries:
            if time_entry.is_closed():
                start = datetime.fromisoformat(time_entry.start_time)
                end = datetime.fromisoformat(time_entry.end_time)
                delta = end - start

                if period == "daily":
                    key = self._daily_key(start.date())
                elif period == "weekly":
                    key = self._weekly_key(start.date())
                elif period == "monthly":
                    key = self._monthly_key(start.date())
                else:
                    print("Invalid period")
                    return

                period_summary[key][time_entry.role_name] += delta

        print(f'{period} summary for "{project.name}"')
        for key, role_names in sorted(period_summary.items()):
            print(f"\n{key}:")
            for role_name, total_time in role_names.items():
                total_hours = total_time.total_seconds() / 3600
                formatted_total_time = f"{total_hours:.2f}"
                print(f"  {role_name}: {formatted_total_time}")

    def _daily_key(self, start_date: date) -> str:
        weekday_name = start_date.strftime("%A")
        return f"{start_date} ({weekday_name})"

    def _weekly_key(self, start_date: date) -> str:
        # Get the date of the beginning of the week
        start_of_week = start_date - timedelta(days=start_date.weekday())
        start_of_week_str = start_of_week.strftime("%Y-%m-%d")
        week_number = start_date.isocalendar()[1]
        return f"{start_of_week_str} ({week_number})"

    def _monthly_key(self, start_date: date) -> str:
        start_of_month = start_date.replace(day=1)
        month_name = start_of_month.strftime("%B")
        return f"{start_of_month} ({month_name})"
