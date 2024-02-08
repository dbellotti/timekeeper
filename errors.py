class ProjectNotFoundError(Exception):
    """Exception raised when a project is not found."""

    def __init__(self, project_name: str):
        self.project_name = project_name
        super().__init__(f'Project "{project_name}" does not exist.')


class RoleNotFoundError(Exception):
    """Exception raised when a role is not found."""

    def __init__(self, role_name: str):
        self.role_name = role_name
        super().__init__(f'Role "{role_name}" does not exist.')


class UserQuitException(Exception):
    """Exception raised when an invalid time is provided."""

    def __init__(self):
        super().__init__("\n...project creation abandoned, goodbye")
