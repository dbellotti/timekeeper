import json
import os
import shutil
import unittest
from datetime import datetime
from unittest.mock import patch

from adapters import ProjectFileRepository
from entities import Project, Role, TimeEntry
from use_cases import InitializeProjectWizard, StartTracking


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
        role = Role(name="el jefe", hourly_rate=100)
        time_entry = TimeEntry(role_name=role.name, start_time=dt)
        project = Project(name="timekeeper", roles=[role], time_entries=[time_entry])

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
    def setUp(self) -> None:
        self.repo_dirname = "test_repo"

    def tearDown(self) -> None:
        destroy_repo(self.repo_dirname)

    @patch("builtins.print")
    @patch(
        "use_cases.StartTracking._get_datetime",
        return_value=datetime(2023, 1, 1, 12, 0),
    )
    def test_execute(self, mock_datetime, mock_print) -> None:
        project = Project(name="some-project")
        project.add_role(Role(name="some-role", hourly_rate=100))
        repo = ProjectFileRepository(self.repo_dirname)
        repo.save(project)
        StartTracking(repo).execute(project.name)
        project = repo.load(project.name)
        self.assertEqual(len(project.time_entries), 1)
        self.assertEqual(project.time_entries[0].role_name, "some-role")
        self.assertEqual(
            project.time_entries[0].start_time, str(datetime(2023, 1, 1, 12, 0, 0))
        )
        self.assertIsNone(project.time_entries[0].end_time)


if __name__ == "__main__":
    unittest.main()
