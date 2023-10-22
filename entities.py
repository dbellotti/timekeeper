from dataclasses import dataclass, field


@dataclass
class Role:
    name: str
    hourly_rate: int


@dataclass
class TimeEntry:
    role_name: str
    start_time: str
    end_time: str = ""


@dataclass
class Project:
    name: str
    roles: list[Role] = field(default_factory=list)
    time_entries: list[TimeEntry] = field(default_factory=list)

    def __str__(self) -> str:
        return self.name

    def add_role(self, role: Role):
        self.roles.append(role)

    def add_time_entry(self, time_entry: TimeEntry):
        self.time_entries.append(time_entry)

    def last_time_entry_is_open(self):
        return self.time_entries[-1].end_time is None
