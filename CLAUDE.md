# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Timekeeper is a CLI time tracking tool that follows Clean Architecture principles. Users track time on projects with role-based hourly rates, storing data in customizable "vault" directories as readable JSON files.

## Development Commands

```bash
# Setup environment
devbox shell

# Run tests
python -m unittest
# OR
devbox run test

# Lint and format
ruff check
ruff format

# Type checking
mypy timekeeper/

# Install locally for testing
pip install -e .

# Clean up
devbox run clean
```

## Architecture

The codebase uses Clean Architecture with clear layer separation:

**Entities** (`entities.py`): Core domain objects
- `Project`: Main aggregate containing roles and time entries
- `Role`: Name + hourly rate for different project roles  
- `TimeEntry`: Time tracking records with start/end times

**Adapters** (`adapters.py`): External interfaces
- `VaultAdapter`: Abstract storage interface
- `FileVault`: JSON file storage implementation
- `ProjectRegistry`: Global index mapping project names to vault locations

**Use Cases** (`use_cases.py`): Business logic
- `InitializeVault/Project/Role`: Setup workflows
- `ToggleTrackingInteractor`: Start/stop time tracking
- `SummarizeTime`: Generate time reports
- `StartTracking/StopTracking`: Core timing operations

**CLI** (`cli.py`): User interface orchestrating use cases

## Key Concepts

**Vaults**: Storage directories containing project JSON files. Projects can live in different vaults, tracked by a global registry at `~/.config/timekeeper/lookup.json`.

**Multi-Step Initialization**: Project creation follows `InitializeVault` → `InitializeProject` → `InitializeRole` → `SaveProject` chain for better separation of concerns.

## Testing

Tests cover the full stack using Python unittest. Mock file operations and focus on business logic verification. All tests should pass before commits.

## CLI Commands

- `tk init`: Interactive project/role setup
- `tk toggle <project> [role]`: Start/stop tracking
- `tk sum --period [daily|weekly|monthly] --project <name>`: Time reports  
- `tk projects/vaults/index`: List projects, vaults, or show registry
- `tk info <project>`: Check if timer running

## Code Patterns

- Use dependency injection for adapters (pass `VaultAdapter` to use cases)
- Follow existing error handling patterns with custom exceptions in `errors.py`
- Maintain separation between storage logic (`FileVault`) and registry logic (`ProjectRegistry`)
- Interactive wizards should guide users through complex workflows
- Always update the `ProjectRegistry` when creating projects in new vaults