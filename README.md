# timekeeper

Basic time tracking cli for projects and roles. Time entries stored in readable json format.

install locally with `pip install -e .`
```console
$ tk
usage: tk [-h] {init,toggle,sum} ...

Time tracking utility.

positional arguments:
  {init,toggle,sum}
    init             Initialize a new project.
    toggle           Toggle time tracking for a project.
    sum              Summarize time spent on projects.

options:
  -h, --help         show this help message and exit
```

## dependencies

[Devbox](https://www.jetpack.io/devbox/docs/installing_devbox/) is the only dependency, it requires and includes Nix Package Manager.

## develop

```bash
devbox shell
```

### test

```bash
devbox run test
```
