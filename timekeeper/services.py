from timekeeper.adapters import FileVault, ProjectRegistry
from timekeeper.entities import Project
from timekeeper.errors import UserQuitException
from timekeeper.use_cases import (
    InitializeProject,
    InitializeRole,
    InitializeVault,
    SaveProject,
)


class ProjectWorkflowService:
    """Application Service for orchestrating project initialization workflows."""

    def __init__(self):
        self.registry = ProjectRegistry()

    def initialize_project_workflow(self) -> Project:
        """Orchestrates the complete project initialization workflow."""
        vault = InitializeVault(FileVault).execute()

        print()
        project_name = input("Enter project name: ")

        # Handle existing project with globally unique name constraint
        if self.registry.exists(project_name):
            project = self._handle_existing_project(project_name)
        else:
            project = InitializeProject().execute(project_name)

        project = InitializeRole(vault, project).execute()
        project = SaveProject(vault, project).execute()
        self.registry.update_index(vault.base_path, project.name)
        return project

    def _handle_existing_project(self, project_name: str) -> Project:
        """Handle workflow when project already exists globally."""
        print(f"Project {project_name} already exists.")
        action = input(
            "Do you want to add a new role/rate or quit? Enter 'role' to add a role or 'quit' to exit: "
        ).lower()
        if action == "quit":
            raise UserQuitException

        # Load existing project from its vault
        vault_path = self.registry.get_project_vault_path(project_name)
        vault = FileVault(vault_path)
        return vault.load(project_name)
