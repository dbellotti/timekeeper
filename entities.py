from dataclasses import dataclass, field
from datetime import datetime

from errors import RoleNotFoundError


@dataclass
class Role:
    """Represents a role in a project."""

    name: str
    hourly_rate: int


@dataclass
class TimeEntry:
    """Represents a time entry for a role in a project."""

    role_name: str = ""
    start_time: str = ""
    end_time: str = ""

    def now(self) -> datetime:
        return datetime.now()

    def start(self) -> None:
        self.start_time = str(self.now())

    def finish(self) -> None:
        self.end_time = str(self.now())

    def is_open(self) -> bool:
        return self.start_time and self.end_time == ""

    def is_closed(self) -> bool:
        return not self.is_open()

    def __bool__(self) -> bool:
        return any([self.role_name, self.start_time, self.end_time])


@dataclass
class Project:
    """Represents a project with roles and time entries."""

    name: str
    roles: [Role] = field(default_factory=list)
    time_entries: [TimeEntry] = field(default_factory=list)

    def __str__(self) -> str:
        return self.name

    def add_role(self, role: Role) -> None:
        self.roles.append(role)

    def start_time_entry(self, role_name: str) -> None:
        time_entry = TimeEntry(role_name)
        time_entry.start()
        self.time_entries.append(time_entry)

    def end_time_entry(self, role_name: str) -> None:
        time_entry = self.last_time_entry(role_name)
        time_entry.finish()

    def last_time_entry(self, role_name: str = None) -> TimeEntry:
        if role_name:
            # get the time entries by role
            time_entries = [te for te in self.time_entries if role_name == te.role_name]
        else:
            # get the time entries
            time_entries = self.time_entries

        # return the last time entry
        if time_entries:
            return time_entries[-1]
        else:
            return TimeEntry()

    def get_role(self, role_name: str) -> Role:
        if role_name:
            for role in self.roles:
                if role.name == role_name:
                    return role
            raise RoleNotFoundError(role_name)
        else:
            role = self.get_default_role()
            print(f"No role provided, using default role: {role.name}")
            return role

    def get_default_role(self) -> Role:
        return self.roles[0]

    def has_role(self, role_name: str) -> bool:
        return role_name in [role.name for role in self.roles]
