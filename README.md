# timekeeper

A flexible time tracking CLI for projects with role-based hourly rates. Store your time entries in organized "vaults" as readable JSON files.

## Features

- **Custom vault directories**: Store projects in any location (work, personal, client-specific)
- **Role-based tracking**: Multiple roles per project with different hourly rates
- **Flexible time reporting**: Daily, weekly, and monthly summaries
- **Simple CLI**: Easy commands for daily time tracking workflow
- **Readable data**: JSON storage format for easy backup and migration

## Installation

```bash
pip install -e .
```

## Quick Start

```bash
# Initialize a new project (choose vault location interactively)
tk init

# Start/stop time tracking
tk toggle my-project developer

# View time summaries
tk sum --period weekly --project my-project

# Check if timer is running
tk info my-project

# List all projects
tk projects
```

## Available Commands

```console
$ tk --help
usage: tk [-h] {init,toggle,t,sum,s,info,add_role,projects,p,vaults,v,index,i} ...

Time tracking utility.

positional arguments:
  init                 Initialize a new project
  toggle (t)           Toggle time tracking for a project
  sum (s)              Summarize time spent on projects
  info                 Show project info
  add_role             Add a role to an existing project
  projects (p)         List all projects
  vaults (v)           List all vault directories
  index (i)            Show the project registry

options:
  -h, --help           show this help message and exit
```

## Vault System

Timekeeper uses "vaults" to organize your projects:

- **Vault**: A directory containing project JSON files
- **Global registry**: Tracks which projects live in which vaults
- **Multiple vaults**: Organize projects by context (work, personal, clients)
- **Unique names**: Project names are globally unique across all vaults

Example vault structure:
```
~/work-projects/        # Work vault
├── client-a.json
├── client-b.json
└── internal-tools.json

~/personal-projects/    # Personal vault  
├── side-project.json
└── learning.json
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
