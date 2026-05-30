# ShortcutXL Installation

## Requirements

- **Windows 10/11** with **Excel 2016+** (64-bit)
- **Node.js >= 20**

## Steps

### 1. Open Command Prompt or PowerShell and install Node.js

```bash
winget install OpenJS.NodeJS.LTS --source winget
```

Then close and reopen your terminal.

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

To authenticate Shortcut from the terminal after setup:

```bash
shortcut login
```

## Running Through Another Agent

After the initial interactive setup, another agent can invoke ShortcutXL through the plugin with commands like:

```bash
shortcut --skip-spreadsheet-permissions --skip-runtime-permissions -p "Build a summary model from the open workbook"
shortcut --session a1b2c3d4 --skip-spreadsheet-permissions --skip-runtime-permissions -p "Export the summary to PDF"
```

Use `--skip-runtime-permissions` only when the task actually needs runtime filesystem or shell access. Before using it, the agent should confirm with the user that ShortcutXL may bypass runtime filesystem and shell approvals for that run.

Flag contract for ShortcutXL print-mode use:

- `--skip-spreadsheet-permissions`: ShortcutXL print-mode spreadsheet auto-approval only. This should normally be present for spreadsheet reads/writes in print mode.
- `--skip-runtime-permissions`: bypass runtime filesystem and shell approval checks. In ShortcutXL print mode, this is also what allows subagent spawn without an approval UI.
- If the task may need local file search/open/save/export, shell commands, subagents, VBA/module work, or broad workbook cleanup, use both flags together after confirmation.
- Before using `--skip-runtime-permissions` by itself or together with `--skip-spreadsheet-permissions`, confirm with the user that bypassing runtime filesystem and shell approvals for that run is acceptable.

```bash
shortcut --skip-spreadsheet-permissions --skip-runtime-permissions -p "Build a summary model from the open workbook"
shortcut --skip-spreadsheet-permissions --skip-runtime-permissions -p "Use subagents to analyze this workbook and apply the fixes"
```
