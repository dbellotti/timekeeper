import os
from collections import defaultdict
from datetime import datetime, timedelta

from adapters import ProjectFileRepository
from entities import Project, Role, TimeEntry
from errors import UserQuitException


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
                raise UserQuitException
            return self.project_repo.load(project_name)
        return Project(name=project_name)

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
    def __init__(self, project_repo: str) -> None:
        self.project_repo = project_repo

    def execute(self, project_name: str, role_name: str) -> None:
        project = self.project_repo.load(project_name)
        role = project.get_role(role_name)

        if project.last_time_entry(role.name).is_open():
            StopTracking.execute(project, role)
        else:
            StartTracking.execute(project, role)

        self.project_repo.save(project)


class StartTracking:
    def execute(project: Project, role: Role) -> None:
        time_entry = TimeEntry(role.name)
        time_entry.start()
        project.start_time_entry(time_entry)
        print(f"Started tracking at {time_entry.start_time}")


class StopTracking:
    def execute(project: Project, role: Role) -> None:
        time_entry = project.last_time_entry(role.name)
        time_entry.finish()
        print(f"Stopped tracking at {time_entry.end_time}")


class SummarizeTime:
    def __init__(self, project_repo: ProjectFileRepository) -> None:
        self.project_repo = project_repo

    def execute(self, period: str, project_name: str, precise=False) -> None:
        project = self.project_repo.load(project_name)
        period_summary = defaultdict(lambda: defaultdict(timedelta))

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

        print(f'{period} summary for "{project_name}"')
        for key, role_names in sorted(period_summary.items()):
            print(f"\n{key}:")
            for role_name, total_time in role_names.items():
                total_hours = total_time.total_seconds() / 3600
                formatted_total_time = f"{total_hours:.2f}"
                print(f"  {role_name}: {formatted_total_time}")

    def _daily_key(self, start_date: datetime) -> datetime:
        weekday_name = start_date.strftime("%A")
        return f"{start_date} ({weekday_name})"

    def _weekly_key(self, start_date: datetime) -> str:
        # Get the date of the beginning of the week
        start_of_week = start_date - timedelta(days=start_date.weekday())
        start_of_week_str = start_of_week.strftime("%Y-%m-%d")
        week_number = start_date.isocalendar()[1]
        return f"{start_of_week_str} ({week_number})"

    def _monthly_key(self, start_date: datetime) -> datetime:
        start_of_month = start_date.replace(day=1)
        month_name = start_of_month.strftime("%B")
        return f"{start_of_month} ({month_name})"
