# timekeeper

Basic time tracking cli for projects and roles. Time entries stored in readable json format.

```console
$ python3 ./main.py --help
usage: main.py [-h] {init,toggle,sum} ...

Time tracking utility.

positional arguments:
  {init,toggle,sum}
    init             Initialize a new project.
    toggle           Toggle time tracking for a project.
    sum              Summarize time spent on projects.

options:
  -h, --help         show this help message and exit
```

## develop

Nix shell available for convenience. [install nix](https://github.com/DeterminateSystems/nix-installer) (with flakes enabled).

```bash
nix develop
```

### test

```bash
python3 -m unittest
```
