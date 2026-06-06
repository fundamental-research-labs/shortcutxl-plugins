# ShortcutXL Skill

Control [ShortcutXL](https://shortcut.ai) — an AI-powered Excel agent — from Codex or Claude Code.

## Install (Codex)

Inside a Codex session:

```
$skill-installer install https://github.com/fundamental-research-labs/shortcutxl-plugins/tree/master/shortcutxl
```

Then restart Codex.

## Install (Claude Code)

```
/plugin marketplace add fundamental-research-labs/shortcutxl-plugins
/plugin install shortcutxl@shortcut
```

## Manual install

Copy the `shortcutxl/` directory to `~/.agents/skills/shortcutxl/` and restart your agent.

## Using It From Another Agent

The plugin teaches the coding agent to run `shortcut` for spreadsheet work and to preserve the returned session id on follow-up calls.

- ShortcutXL runs non-interactively when invoked with `-p` / `--print`, so use `--skip-spreadsheet-permissions` for spreadsheet reads/writes in print mode.
- Use `--skip-runtime-permissions` only when the task actually needs runtime filesystem or shell access, such as searching/opening/saving files, shell-backed operations, exports, subagents, or broad workbook cleanup that may cross those boundaries.
- Before using runtime bypass, confirm with the user that runtime filesystem and shell approval bypass is acceptable.
- After confirmation, use both flags: `--skip-spreadsheet-permissions --skip-runtime-permissions`.
- `--skip-runtime-permissions` is the important flag for ShortcutXL's bash/file/subagent capability in print mode.

Examples:

```bash
shortcut --skip-spreadsheet-permissions --skip-runtime-permissions -p "Create a DCF model for AAPL"
shortcut --session a1b2c3d4 --skip-spreadsheet-permissions --skip-runtime-permissions -p "Export the finished workbook to PDF on my Desktop"
shortcut --skip-spreadsheet-permissions --skip-runtime-permissions -p "Use subagents to analyze this workbook and make the fixes"
```

## Sync

Source of truth is `shortcutXL/runtime/plugins/` in the monorepo. To sync to the published repo:

```bash
cd shortcutXL/runtime/plugins
cp -r .claude-plugin .agents shortcutxl README.md /path/to/shortcutxl-plugins/
```

If you changed install, permissioning, or agent-usage copy in `shortcutXL/runtime/user-docs/`, regenerate the published docs artifacts before shipping:

```bash
cd ../runtime
pnpm run build:user-docs
```
