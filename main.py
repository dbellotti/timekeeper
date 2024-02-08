import argparse

from adapters import ProjectFileRepository
from use_cases import InitializeProjectWizard, SummarizeTime, ToggleTrackingInteractor


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
            "role", type=str, help="The role you want to tracking time for.", nargs="?"
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

        args = parser.parse_args()

        if args.command == "init":
            self.init_project()
        elif args.command == "toggle":
            self.toggle_tracking(args.project_name, args.role)
        elif args.command == "sum":
            self.summarize_time(args.period, args.project)
        else:
            parser.print_help()

    def init_project(self) -> None:
        InitializeProjectWizard(self.project_repo).execute()

    def toggle_tracking(self, project_name: str, role_name: str = None) -> None:
        ToggleTrackingInteractor(self.project_repo).execute(project_name, role_name)

    def summarize_time(self, period: str, project_name: str = None) -> None:
        SummarizeTime(self.project_repo).execute(period, project_name)


if __name__ == "__main__":
    try:
        cli = CommandLineInterface()
        cli.run()
    except Exception as e:
        exit(e)
