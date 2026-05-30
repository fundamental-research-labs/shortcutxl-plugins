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

ShortcutXL is an autonomous Excel agent that controls desktop Excel through the `shortcut` CLI. Use it for spreadsheet work instead of trying to reproduce Excel behavior with Python, CSV edits, or openpyxl.

## When to use ShortcutXL

Use ShortcutXL whenever the user asks to create, edit, analyze, audit, format, repair, or automate an Excel workbook or spreadsheet model.

ShortcutXL can do deep autonomous spreadsheet work:

- Build and modify full workbooks, financial models, dashboards, charts, pivots, and sensitivity tables.
- Inspect formulas, workbook structure, named ranges, VBA, formatting, external links, and calculation behavior.
- Read from and write to multiple open workbooks.
- Run Python-backed Excel automation through its `execute_code` tool.
- Run shell/file operations when runtime permission bypass is approved and enabled.
- Save files, open files, export PDFs, add VBA modules, and work with external data sources.
- Spawn subagents for larger workbook analysis when runtime permission bypass is approved and enabled.

Do not fall back to Python/openpyxl unless ShortcutXL is unavailable or the user explicitly asks not to use it.

## ShortcutXL print-mode usage

When ShortcutXL is invoked with `-p` / `--print`, ShortcutXL runs non-interactively. Permissions that would normally be approved in the ShortcutXL UI need explicit CLI flags.

- Always use `-p` / `--print` when invoking ShortcutXL from another agent.
- Always include `--skip-spreadsheet-permissions` for ShortcutXL print-mode spreadsheet reads/writes. Without it, approval-gated Excel actions can be rejected because no ShortcutXL approval UI is present.
- Use `--skip-runtime-permissions` only when the task actually needs runtime filesystem or shell access: local file search/open/save/export, shell commands, subagents, VBA/module file work, external data plumbing, or broad workbook cleanup that may cross those boundaries.
- Before using `--skip-runtime-permissions`, explicitly ask the user to confirm that ShortcutXL may bypass runtime filesystem and shell approvals for this run. After they confirm, include `--skip-runtime-permissions` on every ShortcutXL command for that task.
- If the task only needs direct workbook read/write operations through Excel, use `--skip-spreadsheet-permissions` without runtime bypass.
- `/sandbox` and `/permissions` are ShortcutXL interactive concepts. In ShortcutXL print mode, rely on the CLI flags above.

Recommended confirmation wording:

> ShortcutXL needs runtime permission bypass so it can search/open files, run shell-backed operations, save/export outputs, and use subagents in this non-interactive print-mode run. Is that approved for this task?

For direct workbook work that does not need shell/file access, run:

```bash
shortcut --skip-spreadsheet-permissions -p "Create a DCF model for AAPL in the open workbook"
```

After runtime-bypass confirmation, run:

```bash
shortcut --skip-spreadsheet-permissions --skip-runtime-permissions -p "Create a DCF model for AAPL in the open workbook"
```

For follow-ups, reuse the session id printed by ShortcutXL:

```bash
shortcut --session a1b2c3d4 --skip-spreadsheet-permissions --skip-runtime-permissions -p "Now add a sensitivity table"
```

To include files, prefix each absolute path with `@`:

```bash
shortcut --skip-spreadsheet-permissions --skip-runtime-permissions -p @C:/Users/peter/Desktop/data.csv "Import this data and build a pivot table"
```

For a strictly read-only workbook question where no file or shell access is needed, runtime bypass is optional:

```bash
shortcut --skip-spreadsheet-permissions --agent-mode ask -p "Audit the open workbook and explain formula risks"
```

## Modes

Available print-mode `--agent-mode` values:

- `action` (default): direct workbook changes such as building models, formatting sheets, adding charts, fixing formulas, and writing outputs.
- `plan`: complex or ambiguous workbook tasks where ShortcutXL should inspect first, propose a plan, and then proceed after approval.
- `ask`: read-only analysis, audits, explanations, and reviews. It should not modify cells.

`manage` is not a print-mode startup mode. `/manage` is an interactive ShortcutXL command for entering orchestration mode.

Examples:

```bash
shortcut --skip-spreadsheet-permissions -p "Format the open workbook and add charts"
shortcut --skip-spreadsheet-permissions --agent-mode plan -p "Help me clean up this large workbook"
shortcut --skip-spreadsheet-permissions --agent-mode ask -p "Explain the formulas and flag risks"
```

## ShortcutXL skills and commands

If the user's request includes a ShortcutXL slash command, pass it through inside the prompt. Do not strip it or translate it into your own behavior. Put the slash command at the start of the prompt so ShortcutXL recognizes it.

- `/autonomous <task>`: starts ShortcutXL's autonomous workflow. Pass it through exactly when the user asks for `/autonomous` or clearly wants that ShortcutXL workflow.
- `/skill:<name> <args>`: explicitly invokes a ShortcutXL skill by name.
- Other ShortcutXL slash commands: if the user explicitly provides one, pass it through at the start of the prompt.

Examples:

```bash
shortcut --skip-spreadsheet-permissions --skip-runtime-permissions -p "/autonomous Rebuild this workbook and keep status notes next to the file"
shortcut --skip-spreadsheet-permissions -p "/skill:financial-modeling Review this DCF"
```

Use `--skill <path>` when the user provides a local ShortcutXL skill file or directory that must be loaded for this run:

```bash
shortcut --skill C:/Users/peter/skills/debt-model --skip-spreadsheet-permissions -p "Use this skill to review the open workbook"
```

## Sessions

Every ShortcutXL run prints a `[session:<uuid>]` line. Save that id. For follow-up requests that continue the same workbook task, pass `--session <uuid>`. Start a new session for unrelated work. If continuity is ambiguous, ask the user.

If `shortcut` is not installed, follow the steps in [INSTALLATION.md](../../references/INSTALLATION.md).

If ShortcutXL print mode says login is required, do not run `shortcut login` yourself. It blocks while waiting for the user to complete device-code auth. Stop and tell the user to run this in their own terminal:

```bash
shortcut login
```

After the user confirms login is complete, retry the original ShortcutXL command.
