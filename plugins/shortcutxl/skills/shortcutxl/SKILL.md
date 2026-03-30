---
name: shortcutxl
description: Run ShortcutXL, an AI Excel agent that controls desktop Excel. Use this to build spreadsheets, analyze data, create financial models, and automate Excel tasks via the `shortcut` CLI.
---

# ShortcutXL

An AI agent that lives on your computer and has Excel superpowers.

## Requirements

- **Windows 10/11** with **Excel 2016+** (64-bit)
- **Node.js >= 20**

## Install

### 1. Open Command Prompt or PowerShell and install Node.js

```bash
winget install OpenJS.NodeJS.LTS
```

### 2. Install ShortcutXL

```bash
npm install -g shortcutxl
```

### 3. Launch ShortcutXL

```bash
shortcut
```

First launch runs an automated setup (Git, Python packages, Excel add-in registration, etc.) and prompts the user to open Excel. After setup, authenticate with `/login` inside the TUI.

**Important:** First launch must be interactive — do NOT run with `-p`. The user must run `shortcut` in a terminal and follow the prompts.

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

### Run a task (non-interactive)

```bash
shortcut -p "Create a DCF model for AAPL"
```

`-p` / `--print` runs the task and exits. Without it, Shortcut opens an interactive TUI session.

### Continue a session

```bash
shortcut -c "Now add a sensitivity table"
```

### Resume a past session

```bash
shortcut -r
```

### Include files in the prompt

Prefix with `@`:

```bash
shortcut -p @data.csv "Import this into Excel and create a pivot table"
shortcut -p @requirements.md @template.xlsx "Build this spreadsheet"
```

### Pipe stdin

Stdin auto-enables print mode:

```bash
echo "Summarize the open workbook" | shortcut
```

### JSON output (structured)

```bash
shortcut --mode json --no-session "What formulas are in A1:A10?" 2>/dev/null
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

If the user hasn't set up ShortcutXL yet, walk them through the 3 install steps above.
