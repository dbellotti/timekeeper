import argparse
import json

from timekeeper.adapters import ProjectFileStorage, ProjectIndex
from timekeeper.config import get_projects_path
from timekeeper.use_cases import (
    InitializeProjectWizard,
    SummarizeTime,
    ToggleTrackingInteractor,
)


class CommandLineInterface:
    def run(self):
        parser = argparse.ArgumentParser(description="Time tracking utility.")
        subparsers = parser.add_subparsers(dest="command")

        # init subcommand
        subparsers.add_parser("init", help="Initialize a new project.")

        # toggle subcommand
        parser_toggle = subparsers.add_parser(
            "toggle", help="Toggle time tracking for a project.", aliases=["t"]
        )
        parser_toggle.add_argument(
            "project_name", type=str, help="Name of the project."
        )
        parser_toggle.add_argument(
            "role", type=str, help="The role you want to tracking time for.", nargs="?"
        )

        # sum subcommand
        parser_sum = subparsers.add_parser(
            "sum", help="Summarize time spent on projects.", aliases=["s"]
        )
        parser_sum.add_argument(
            "--period",
            choices=["daily", "weekly", "monthly"],
            default="weekly",
            help="Summary period.",
        )
        parser_sum.add_argument(
            "--project", type=str, help="Display sum for specific project."
        )

        # helper subcommands
        subparsers.add_parser("projects", help="List all projects.", aliases=["p"])
        subparsers.add_parser("vaults", help="List all vaults.", aliases=["v"])
        subparsers.add_parser("index", help="Show the timekeeper index.", aliases=["i"])

        args = parser.parse_args()

        if args.command == "init":
            self.init_project()
        elif args.command in ["toggle", "t"]:
            self.toggle_tracking(args.project_name, args.role)
        elif args.command in ["sum", "s"]:
            self.summarize_time(args.period, args.project)
        elif args.command in ["projects", "p"]:
            print(ProjectIndex().list_projects())
        elif args.command in ["vaults", "v"]:
            print(ProjectIndex().list_vaults())
        elif args.command in ["index", "i"]:
            print(json.dumps(ProjectIndex().get_index(), indent=2))
        else:
            parser.print_help()

    def init_project(self) -> None:
        default_path = get_projects_path()
        project_path = (
            input(
                f"Where would you like your project to be stored? Press Enter to use {default_path}: ",
            )
            or default_path
        )
        project_storage = ProjectFileStorage(project_path)
        project = InitializeProjectWizard(project_storage).execute()
        ProjectIndex().update_index(project_storage.base_path, project.name)

    def toggle_tracking(self, project_name: str, role_name: str = "") -> None:
        vault_path = ProjectIndex().get_project_vault_path(project_name)
        project_storage = ProjectFileStorage(vault_path)
        # TODO try to replace usage of the storage with the project object
        # project = ProjectFileStorage(vault_path).load(project_name)
        ToggleTrackingInteractor(project_storage).execute(project_name, role_name)

    def summarize_time(self, period: str, project_name: str = "") -> None:
        vault_path = ProjectIndex().get_project_vault_path(project_name)
        project = ProjectFileStorage(vault_path).load(project_name)
        SummarizeTime().execute(period, project)


def main():
    try:
        cli = CommandLineInterface()
        cli.run()
    except Exception as e:
        exit(str(e))


if __name__ == "__main__":
    main()
