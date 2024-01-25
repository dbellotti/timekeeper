import argparse

from adapters import ProjectFileRepository
from use_cases import (
    InitializeProjectWizard,
    ProjectNotFoundError,
    RoleNotFoundError,
    SummarizeTime,
    ToggleTrackingInteractor,
    UserQuitException,
)


class CommandLineInterface:
    def __init__(self):
        self.project_repo = ProjectFileRepository(".timekeeper")

    def run(self):
        parser = argparse.ArgumentParser(description="Time tracking utility.")
        subparsers = parser.add_subparsers(dest="command")

        # init subcommand
        subparsers.add_parser("init", help="Initialize a new project.")

        # toggle subcommand
        parser_toggle = subparsers.add_parser(
            "toggle", help="Toggle time tracking for a project."
        )
        parser_toggle.add_argument(
            "project_name", type=str, help="Name of the project."
        )
        parser_toggle.add_argument(
            "role", type=str, help="The role you want to tracking time for."
        )

        # sum subcommand
        parser_sum = subparsers.add_parser(
            "sum", help="Summarize time spent on projects."
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
        parser_sum.add_argument(
            "--precise", action="store_true", help="Display sum in ISO time format."
        )

        args = parser.parse_args()

        if args.command == "init":
            self.init_project()
        elif args.command == "toggle":
            # TODO
            # make sure saving does a complete replace instead of append
            # handle non default roles
            self.toggle_tracking(args.project_name)
        elif args.command == "sum":
            # TODO
            self.summarize_time(args.period, args.project, args.precise)
        else:
            parser.print_help()

    def init_project(self):
        try:
            InitializeProjectWizard(self.project_repo).execute()
        except UserQuitException as e:
            print()
            exit(e)

    def toggle_tracking(self, project_name):
        ToggleTrackingInteractor(self.project_repo).execute(project_name)

    def summarize_time(self, period, project_name=None, precise=False):
        SummarizeTime(self.project_repo).execute(period, project_name, precise)


if __name__ == "__main__":
    try:
        cli = CommandLineInterface()
        cli.run()
    except Exception as e:
        print(e)
        exit(1)
