# Roadmap: Timekeeper → Agent Work Orchestration CLI

## The Premise

Timekeeper already solves a real problem for humans: tracking time on projects.
But its Clean Architecture — vaults, projects, roles, entries, a global registry —
maps almost 1:1 onto a harder, unsolved problem: **giving agents persistent,
structured memory and coordination primitives**.

Today, agents (LLMs doing agentic work) have no native way to:

- Remember what they did in a previous session
- Leave structured notes for their future selves
- Coordinate with other agent instances on shared work
- Checkpoint progress on long-running tasks
- Record what was tried, what failed, and why
- Track dependencies between units of work

This roadmap proposes evolving Timekeeper into a tool that agents can call
themselves — a CLI that becomes the "working memory" and "task ledger" for
agentic workflows, while remaining useful (and readable) for humans.

---

## Design Principles

1. **Machine-readable, human-inspectable.** Everything stays in JSON files in
   vaults. Humans can always `cat` a file and understand what's happening. But
   the schema is structured enough for agents to parse reliably.

2. **CLI-first, pipe-friendly.** Every command produces structured output
   (JSON via `--json` flag) so agents can consume it programmatically. No
   interactive prompts in the agent-facing codepath.

3. **Build on what exists.** The entity model, vault system, and registry are
   sound. We extend, not rewrite.

4. **Useful at every phase.** Each milestone is independently valuable. No
   milestone is a "foundation that only pays off later."

---

## Concept Mapping

| Timekeeper Today     | Agent Evolution             |
|----------------------|-----------------------------|
| Project              | **Task** (unit of work)     |
| Role                 | **Agent** (who does work)   |
| TimeEntry            | **WorkSession** (with logs) |
| Vault                | **Workspace** (shared context) |
| ProjectRegistry      | **Task Registry** (global state) |
| hourly_rate          | **cost_per_token / budget**  |

---

## Phase 1: Non-Interactive Mode & Structured Output

**Goal:** Make Timekeeper callable by agents without human interaction.

Today, `tk init` requires interactive prompts. Agents can't use that. Every
command needs a fully non-interactive path.

### Changes

- **`--json` global flag**: All commands output structured JSON to stdout.
  Errors go to stderr. Exit codes are meaningful (0 success, 1 user error,
  2 system error).

- **Non-interactive `init`**:
  ```
  tk init --project myproject --role developer --rate 100 --vault ./work
  ```

- **Non-interactive `add_role`**:
  ```
  tk add_role myproject --role reviewer --rate 80
  ```

- **Quiet mode (`-q`)**: Suppress human-friendly messages, output only data.

- **`tk status <project> --json`**: Machine-readable project state: current
  timer status, last entry, open entries, role list.

### Why This Matters

This is table stakes. Without non-interactive mode, agents literally cannot
use the tool. But it also benefits human power users who want to script
Timekeeper.

---

## Phase 2: Work Sessions with Context

**Goal:** Evolve TimeEntry from "start/end timestamps" into rich work sessions
that carry context.

### New Entity: `WorkSession`

```python
@dataclass
class WorkSession:
    id: str                     # UUID
    agent: str                  # Who did the work (role/agent name)
    start_time: str             # ISO datetime
    end_time: str               # ISO datetime (empty if active)
    status: str                 # "active", "completed", "blocked", "failed"
    intent: str                 # What this session set out to do
    outcome: str                # What actually happened (filled on close)
    artifacts: list[str]        # Files created/modified
    notes: list[str]            # Freeform observations during work
    parent_session: str         # Optional: session this continues from
    tags: list[str]             # Categorization
```

### New Commands

- **`tk start <project> [agent] --intent "Implement login endpoint"`**:
  Opens a session with declared intent.

- **`tk note <project> "Found that auth module uses JWT not sessions"`**:
  Append a note to the active session. Agents use this to leave breadcrumbs.

- **`tk artifact <project> src/auth.py`**:
  Register a file as an artifact of the current session.

- **`tk stop <project> --outcome "Implemented login, tests passing" --status completed`**:
  Close session with outcome. Status can be `completed`, `blocked`, or `failed`.

- **`tk log <project> [--last N] [--json]`**:
  Show work session history. The critical "what happened before me" command.

### Why This Matters

This is the single most valuable addition for agents. When I (an agent) start
a new session on a codebase, the first thing I need is: *what was the last
agent doing, what did they accomplish, what's still open, and what files did
they touch?* `tk log myproject --last 3 --json` answers all of that in one
call.

---

## Phase 3: Task State & Dependencies

**Goal:** Add first-class task tracking — not just "what time was spent" but
"what work needs doing."

### New Entity: `Task`

```python
@dataclass
class Task:
    id: str                     # Short human-readable ID (e.g., "T-001")
    title: str                  # Brief description
    description: str            # Detailed specification
    status: str                 # "pending", "active", "blocked", "done", "failed"
    priority: int               # 1 (highest) to 5 (lowest)
    assigned_agent: str         # Who's responsible
    depends_on: list[str]       # Task IDs that must complete first
    blocked_reason: str         # Why it's blocked (if status=blocked)
    sessions: list[str]         # WorkSession IDs linked to this task
    created_at: str
    updated_at: str
    tags: list[str]
```

### New Commands

```bash
# Task lifecycle
tk task add <project> "Implement user auth" --priority 1 --agent claude
tk task list <project> [--status pending|active|blocked] [--json]
tk task show <project> T-001 --json
tk task update <project> T-001 --status blocked --reason "Waiting on DB schema"
tk task done <project> T-001

# Dependencies
tk task dep <project> T-002 --depends-on T-001

# Link sessions to tasks
tk start <project> --task T-001 --intent "Working on user auth"
```

### Why This Matters

Agents frequently work on multi-step problems. Today, the human has to hold
the task graph in their head and tell the agent what to do next. With
first-class tasks, an agent can:

1. Read the task list at session start
2. Pick the highest-priority unblocked task
3. Work on it, recording a session
4. Mark it done or blocked
5. Move to the next task

This is the primitive that makes "leave an agent running overnight on a
backlog" actually work.

---

## Phase 4: Multi-Agent Coordination

**Goal:** Let multiple agents work in the same workspace without stepping on
each other.

### Mechanisms

- **Lock files**: `tk lock <project> <task-id> --agent claude-1` claims
  exclusive work on a task. Other agents see it's taken and pick something
  else. Locks expire after a configurable timeout (default: 30min) to handle
  crashed agents.

- **Handoff protocol**:
  ```bash
  # Agent A finishes and hands off
  tk stop myproject --outcome "Auth endpoint done, needs review" --handoff

  # Agent B picks up
  tk handoff myproject --json
  # Returns: last session context, open tasks, any notes left
  ```

- **Agent roster**: Track which agents are registered for a project,
  their capabilities, and current status.
  ```bash
  tk agent register <project> claude-code --capabilities "python,testing,refactoring"
  tk agent list <project> --json
  tk agent status <project> claude-code  # active/idle/offline
  ```

### Why This Matters

The future of agent work is not one agent doing everything — it's specialized
agents collaborating. A coding agent, a testing agent, a review agent. They
need a shared ledger of work state. Timekeeper's vault system is already a
shared filesystem-based state store. Adding coordination primitives makes it
a lightweight orchestration layer.

---

## Phase 5: Budgets, Costs & Guardrails

**Goal:** Resource-aware agent work — agents that know their budget and can
self-limit.

### Changes

- **Budget tracking per project/task**:
  ```bash
  tk budget set <project> --max-cost 50.00 --max-sessions 10
  tk budget check <project> --json
  # Returns: { "remaining_cost": 32.50, "remaining_sessions": 7, "ok": true }
  ```

- **Session cost recording**:
  ```bash
  tk stop <project> --cost 2.35 --tokens-used 150000
  ```

- **Guardrails**:
  ```bash
  tk guard <project> --max-files 20 --no-delete --protected "*.env,secrets/*"
  tk guard check <project> src/auth.py --json
  # Returns: { "allowed": true }
  ```

- **Auto-stop on budget exhaustion**: When `tk start` runs, it checks budget.
  If exhausted, it refuses to open a session and exits non-zero. The agent
  framework catches this and escalates to a human.

### Why This Matters

Unsupervised agents need boundaries. Today those boundaries live in the
orchestration framework. Putting them in the shared state store means *any*
agent (regardless of framework) respects the same limits. The human sets
the budget once in the vault, and every agent checks it.

---

## Phase 6: Event Hooks & Integration

**Goal:** Make Timekeeper reactive — things happen when work state changes.

### Mechanisms

- **Hooks**: Shell commands triggered on events.
  ```json
  // .timekeeper/hooks.json in vault
  {
    "on_session_start": "echo 'Agent started' | notify-send",
    "on_session_stop": "python scripts/update_dashboard.py",
    "on_task_blocked": "gh issue comment {task_id} --body '{blocked_reason}'",
    "on_budget_exhausted": "curl -X POST webhook.site/abc123"
  }
  ```

- **Export**: Dump project/session/task data in formats other tools consume.
  ```bash
  tk export <project> --format csv > timesheet.csv
  tk export <project> --format github-issues  # Creates GH issues from tasks
  tk export <project> --format timeline        # Mermaid gantt chart
  ```

- **Watch mode**: `tk watch <project>` tails the vault file and streams
  events as NDJSON. Useful for building dashboards or triggering external
  workflows.

### Why This Matters

Agents don't exist in isolation. They need to report status to humans (Slack,
email), update external systems (GitHub, Jira), and trigger downstream
processes. Hooks turn the vault into an event source.

---

## Implementation Priority & Effort

| Phase | Value to Agents | Value to Humans | Effort | Depends On |
|-------|----------------|-----------------|--------|------------|
| 1. Non-Interactive Mode | Critical | High | Small | Nothing |
| 2. Work Sessions | Critical | Medium | Medium | Phase 1 |
| 3. Task State | High | High | Medium | Phase 2 |
| 4. Multi-Agent Coordination | High | Low | Medium | Phase 3 |
| 5. Budgets & Guardrails | Medium | Medium | Small | Phase 1 |
| 6. Hooks & Integration | Medium | High | Medium | Phase 2 |

**Recommended order**: 1 → 2 → 3 → 5 → 4 → 6

Phase 5 (Budgets) can jump ahead of Phase 4 because it's simple and
immediately useful even with a single agent.

---

## What Stays The Same

- JSON files in vaults. Human-readable. Git-friendly.
- Clean Architecture layers. Use cases stay pure.
- The `tk` CLI entry point. `pip install -e .` workflow.
- Backward compatibility with existing time tracking (`toggle`, `sum`).
- Zero external dependencies (stdlib only) for core functionality.

## What This Becomes

A **lightweight, filesystem-based work orchestration tool** that:

1. Any agent can call via CLI
2. Any human can inspect by reading JSON files
3. Multiple agents can coordinate through without a server
4. Tracks not just *when* work happened, but *what*, *why*, and *what's next*
5. Enforces budgets and guardrails without requiring a centralized controller

The tagline evolves from "track your time" to **"track your work."**

---

## Appendix: A Concrete Agent Workflow

Here's what a real agentic session looks like with the evolved Timekeeper:

```bash
# Human sets up the workspace
tk init --project api-rewrite --role claude-code --rate 0 --vault ./work
tk task add api-rewrite "Migrate users endpoint to v2" --priority 1
tk task add api-rewrite "Migrate orders endpoint to v2" --priority 2
tk task add api-rewrite "Update integration tests" --priority 3 --depends-on T-001,T-002
tk budget set api-rewrite --max-cost 25.00 --max-sessions 20

# Agent starts working
tk budget check api-rewrite --json            # Am I within budget?
tk task list api-rewrite --status pending --json  # What needs doing?
tk start api-rewrite --task T-001 --intent "Migrate users endpoint from v1 to v2"

# During work, the agent leaves breadcrumbs
tk note api-rewrite "Users endpoint has 3 consumers: web, mobile, internal-batch"
tk note api-rewrite "v1 returns snake_case, v2 contract requires camelCase"
tk artifact api-rewrite src/api/v2/users.py
tk artifact api-rewrite tests/api/test_users_v2.py

# Agent finishes
tk stop api-rewrite --outcome "Users v2 endpoint implemented, all 12 tests passing" \
  --status completed --cost 1.80 --tokens-used 95000
tk task done api-rewrite T-001

# Next agent (or same agent, new session) picks up
tk log api-rewrite --last 1 --json            # What just happened?
tk task list api-rewrite --status pending --json  # T-002 is next, T-003 still blocked
tk start api-rewrite --task T-002 --intent "Migrate orders endpoint"
# ...continues...
```

No orchestration framework required. Just a CLI, some JSON files, and
structured discipline.
