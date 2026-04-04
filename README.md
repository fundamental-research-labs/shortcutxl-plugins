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

## Sync

Source of truth is `shortcutXL/shortcutxl-plugins/` in the monorepo. To sync to the published repo:

```bash
cd shortcutXL/shortcutxl-plugins
cp -r shortcutxl README.md /path/to/shortcutxl-plugins/
```
