---
name: shortcutxl
description: Run ShortcutXL, an AI Excel agent that controls desktop Excel. Use this to build spreadsheets, analyze data, create financial models, and automate Excel tasks via the `shortcut` CLI.
license: MIT
compatibility: Requires Windows 10/11 with Excel 2016+ (64-bit) and Node.js >= 20.
metadata:
  author: fundamental-research-labs
  version: "1.0.0"
---

# ShortcutXL

An AI agent that lives on your computer and has Excel superpowers.

## Capabilities

- **Data lives locally** — Workbooks, files, and skills stay on the user's machine.
- **Multi-workbook operations** — Read and write across multiple open workbooks simultaneously.
- **Deep feature control** — Pivots, charts, sensitivity tables, iterative recalculations, and more.
- **VBA access** — Read, write, and run macros. Create VBA modules programmatically.
- **File system access** — Save to arbitrary paths, open files from disk, export PDFs.
- **Extensible** — Integrate any API or data source by adding a skill file or a custom tool extension.
- **User-defined functions (UDFs)** — Custom Excel formulas powered by Python for live data, calculations, or database queries.
- **External data connections** — ODBC, OLE DB, QueryTables, Power Query.

## Usage

### Session management (IMPORTANT)

Every `shortcut` invocation prints a `[session:<uuid>]` line in its output. Remember this UUID for follow-up calls.

**First call** — start a new session:

```bash
shortcut -p "Create a DCF model for AAPL"
# Output will include: [session:a1b2c3d4-...]
```

**Follow-up calls** — if the user's request clearly continues the previous task, use `--session <uuid> -p`:

```bash
shortcut --session a1b2c3d4 -p "Now add a sensitivity table"
```

`--session` accepts a full UUID or a partial prefix (like a git short hash). It opens that session and appends the new prompt to it — no need for `-c`.

If the user's request is clearly unrelated, start a fresh session (no `--session` flag). **If it's ambiguous, ask the user** whether they want to continue the existing session or start a new one.

### Run a task (non-interactive)

```bash
shortcut -p "Create a DCF model for AAPL"
```

`-p` / `--print` runs the task and exits. Without it, Shortcut opens an interactive TUI session.

### Include files in the prompt

Prefix with `@` and use absolute paths (paths are resolved relative to the CLI's cwd, not yours):

```bash
shortcut -p @C:/Users/peter/Desktop/data.csv "Import this into Excel and create a pivot table"
shortcut -p @C:/Users/peter/projects/requirements.md @C:/Users/peter/Desktop/template.xlsx "Build this spreadsheet"
```

### Pipe stdin

Stdin auto-enables print mode:

```bash
echo "Summarize the open workbook" | shortcut
```

### Ephemeral (don't save session)

```bash
shortcut --no-session -p "Quick calculation: NPV at 10% for these cash flows..."
```

## CLI Reference

```
shortcut [options] [@files...] [messages...]
```

### Modes

| Flag | Description |
|------|-------------|
| (default) | Interactive TUI |
| `-p`, `--print` | Run task, print result, exit |
| `--mode json` | NDJSON event stream |
| `-c`, `--continue` | Continue most recent session |
| `-r`, `--resume` | Browse and select a past session |
| `--agent-mode plan` | Start in plan mode (explores workbook, asks questions, proposes a plan before editing) |
| `--agent-mode ask` | Start in ask mode (read-only analysis, review, and audit) |

### Model options

ShortcutXL routes through the Shortcut platform (`agent.shortcut.ai`). Available models:

| Model ID | Name |
|----------|------|
| `claude-opus-4-6` | Claude Opus 4.6 |
| `claude-sonnet-4-6` | Claude Sonnet 4.6 |
| `gpt-5.4-2026-03-05` | GPT-5.4 |

| Flag | Description |
|------|-------------|
| `--model <id>` | Select a model (e.g. `--model claude-sonnet-4-6`) |
| `--model <id>:<thinking>` | Model with thinking level (e.g. `--model claude-sonnet-4-6:high`) |
| `--thinking <level>` | `off`, `minimal`, `low`, `medium`, `high`, `xhigh` |

Users switch models interactively via `/model` or Ctrl+L.

### Session options

| Flag | Description |
|------|-------------|
| `--session <path>` | Use a specific session file or partial UUID |
| `--session-dir <dir>` | Custom session storage directory |
| `--no-session` | Ephemeral mode |

### Tool options

| Flag | Description |
|------|-------------|
| `--tools <list>` | Comma-separated built-in tools: `read`, `bash`, `edit`, `write`, `grep`, `find`, `ls` |
| `--no-tools` | Disable all built-in tools |

### Resource options

| Flag | Description |
|------|-------------|
| `--skill <path>` | Load a skill file or directory |
| `--no-skills` | Disable skill discovery |
| `-e`, `--extension <source>` | Load an extension |
| `--no-extensions` | Disable extension discovery |

### Other

| Flag | Description |
|------|-------------|
| `--system-prompt <text>` | Replace default system prompt |
| `--append-system-prompt <text>` | Append to system prompt |
| `--export <file> [out]` | Export session to HTML |
| `--verbose` | Verbose startup |
| `-h`, `--help` | Help |
| `-v`, `--version` | Version |

### Package management

```bash
shortcut install <source>    # Install a Shortcut package (npm or git)
shortcut remove <source>     # Remove a package
shortcut update              # Update all packages
shortcut list                # List installed packages
shortcut config              # Enable/disable package resources
shortcut uninstall           # Remove registry keys, PATH entry, XLL files
```

## When to use this

Invoke ShortcutXL whenever the user wants to work with Excel or spreadsheets. Claude Code handles code and files; ShortcutXL handles Excel. Run it via `shortcut -p "..."` from bash.

**Choosing the right mode:**

- **Default (action)** — Use for direct tasks: "create a DCF", "format this table", "add a chart". This is the default, no flag needed.
- **`--agent-mode plan`** — Use for complex or ambiguous requests where the agent should explore first: "help me with this workbook", "build a financial model", or when the workbook is large/unfamiliar.
- **`--agent-mode ask`** — Use for read-only questions: "audit this spreadsheet", "explain these formulas", "review this model for errors". The agent will not modify any cells.

```bash
shortcut -p "Create a DCF model for AAPL"
shortcut --agent-mode plan -p "This workbook is a mess, help me fix it"
shortcut --agent-mode ask -p "Audit this financial model for errors"
```

**Session workflow:** The first call prints a `[session:<uuid>]` in the output — remember it. On follow-ups, if the user clearly wants to continue the same task, pass `--session <uuid> -p "..."`. If it's unclear whether they want to continue or start fresh, ask them.

If `shortcut` is not installed, follow the steps in [INSTALLATION.md](../../references/INSTALLATION.md).
