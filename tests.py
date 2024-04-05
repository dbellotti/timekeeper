import json
import os
import shutil
import unittest
from datetime import datetime
from unittest.mock import call, patch

from adapters import ProjectFileRepository
from entities import Project, Role, TimeEntry
from use_cases import (
    InitializeProjectWizard,
    StartTracking,
    StopTracking,
    SummarizeTime,
)


def destroy_repo(repo_dirname):
    if os.path.exists(repo_dirname):
        shutil.rmtree(repo_dirname)


class ProjectFileRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.repo_dirname = "test_repo"

    def tearDown(self):
        destroy_repo(self.repo_dirname)

    def test_init(self):
        self.assertFalse(os.path.exists(self.repo_dirname))
        ProjectFileRepository(self.repo_dirname)
        self.assertTrue(os.path.exists(self.repo_dirname))

    def test_path(self):
        self.assertEqual(
            ProjectFileRepository(self.repo_dirname).path("foo"),
            "test_repo/foo.json",
        )

    def test_save_and_load(self):
        repo = ProjectFileRepository(self.repo_dirname)
        dt = str(datetime.now())
        project = Project(
            name="timekeeper",
            roles=[Role(name="el jefe", hourly_rate=100)],
            time_entries=[TimeEntry(role_name="el jefe", start_time=dt)],
        )

        repo.save(project)
        with open(repo.path(project.name), "r") as f:
            project_dict = json.load(f)

        self.assertDictEqual(
            project_dict,
            {
                "name": "timekeeper",
                "roles": [{"name": "el jefe", "hourly_rate": 100}],
                "time_entries": [
                    {
                        "role_name": "el jefe",
                        "start_time": dt,
                        "end_time": "",
                    }
                ],
            },
        )

        self.assertEqual(project, repo.load(project))


class TimeEntryTests(unittest.TestCase):
    def test_bool(self):
        self.assertFalse(TimeEntry())
        self.assertTrue(TimeEntry(role_name="el jefe"))


class InitializeProjectWizardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_dirname = "test_repo"

    def tearDown(self) -> None:
        destroy_repo(self.repo_dirname)

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["some-project", "some-role", "100"])
    def test_execute(self, mock_input, mock_print) -> None:
        project = InitializeProjectWizard(
            ProjectFileRepository(self.repo_dirname)
        ).execute()
        self.assertEqual(project.name, "some-project")
        self.assertEqual(project.roles[0].name, "some-role")
        self.assertEqual(project.roles[0].hourly_rate, 100)


class StartTrackingTests(unittest.TestCase):
    @patch("builtins.print")
    @patch("entities.TimeEntry.now", return_value=datetime(2023, 1, 1, 12, 0))
    def test_execute(self, mock_datetime, mock_print) -> None:
        project = Project(name="some-project")
        role = Role(name="some-role", hourly_rate=100)
        project.add_role(role)
        StartTracking.execute(project, role)
        entry = project.time_entries[0]
        self.assertEqual(len(project.time_entries), 1)
        self.assertEqual(entry.role_name, "some-role")
        self.assertEqual(entry.start_time, str(datetime(2023, 1, 1, 12, 0, 0)))
        self.assertFalse(entry.end_time)


class StopTrackingTests(unittest.TestCase):
    @patch("builtins.print")
    @patch("entities.TimeEntry.now", return_value=datetime(2023, 1, 1, 12, 0))
    def test_execute(self, mock_datetime, mock_print) -> None:
        project = Project(name="some-project")
        role = Role(name="some-role", hourly_rate=100)
        project.add_role(role)
        StartTracking.execute(project, role)
        StopTracking.execute(project, role)
        entry = project.time_entries[-1]
        self.assertEqual(len(project.time_entries), 1)
        self.assertEqual(entry.role_name, "some-role")
        self.assertEqual(entry.start_time, str(datetime(2023, 1, 1, 12, 0)))
        self.assertEqual(entry.end_time, str(datetime(2023, 1, 1, 12, 0, 0)))


class SummarizeTimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_dirname = "test_repo"
        self.project = Project(name="some-project")
        self.repo = ProjectFileRepository(self.repo_dirname)

    def tearDown(self) -> None:
        destroy_repo(self.repo_dirname)

    @patch("builtins.print")
    def test_execute(self, mock_print):
        self.project.add_role(Role(name="some-role", hourly_rate=100))
        self.project.add_role(Role(name="another-role", hourly_rate=100))
        self.project.time_entries.extend(
            [
                TimeEntry(
                    role_name="some-role",
                    start_time="2023-01-01 12:00:00",
                    end_time="2023-01-01 13:00:00",
                ),
                TimeEntry(
                    role_name="some-role",
                    start_time="2023-01-02 12:00:00",
                    end_time="2023-01-02 13:00:00",
                ),
                TimeEntry(
                    role_name="some-role",
                    start_time="2023-01-03 12:00:00",
                ),
                TimeEntry(
                    role_name="another-role",
                    start_time="2023-01-03 12:00:00",
                    end_time="2023-01-03 13:00:00",
                ),
            ]
        )
        self.repo.save(self.project)

        SummarizeTime(self.repo).execute("daily", self.project.name, True)
        self.assertEqual(
            mock_print.call_args_list,
            [
                call('daily summary for "some-project"'),
                call("\n2023-01-01 (Sunday):"),
                call("  some-role: 1.00"),
                call("\n2023-01-02 (Monday):"),
                call("  some-role: 1.00"),
                call("\n2023-01-03 (Tuesday):"),
                call("  another-role: 1.00"),
            ],
        )
