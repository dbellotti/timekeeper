import os

VAULT_DIRECTORY = "timekeeper"
INDEX_FILENAME = "lookup.json"
PROJECTS_DIRECTORY = "projects"


def config_path():
    root_path = os.path.expanduser("~")
    return os.path.join(root_path, ".config")


def get_projects_path():
    return os.path.join(config_path(), VAULT_DIRECTORY)
