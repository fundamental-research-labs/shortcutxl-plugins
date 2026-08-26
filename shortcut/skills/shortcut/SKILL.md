---
name: shortcut
description: Use Shortcut's cloud spreadsheet tools to create, inspect, modify, save, show, or export workbooks from Codex. Use when the customer explicitly invokes Shortcut for spreadsheet work; do not use for unrelated file or data tasks.
---

# Shortcut

Shortcut is a production workbook host, not a local file-editing fallback. Use the installed `shortcut` MCP tools when they are available. If the remote connection is unavailable, say that Shortcut is not connected; do not claim that a local edit was saved to Shortcut.

## Activation and history

The beta captures supported task-history events only after explicit activation. On the first Shortcut invocation in a task, follow the hook's retention disclosure and ask the customer to re-submit with `Activate Shortcut:` when prompted. Never claim that earlier task history was captured. Installing the plugin alone is not activation.

## Workbook targeting

- Treat attachments as read-only task inputs until the customer opens, creates, selects, or first modifies a workbook.
- Every mutation must target a canonical Shortcut workbook ID. A filename is acceptable only when it identifies one workbook or input unambiguously in the task.
- If several inputs or workbooks match, ask which one. Do not choose by attachment order, visible view, last use, or filename sorting.
- Opening or first modifying an attachment creates a Shortcut working copy and leaves the original attachment unchanged.
- Reading a workbook or supporting document does not import it into the Shortcut library.

## Working and saving

- Work headlessly unless the customer asks to open, show, or manually edit a specific workbook.
- Treat the visible workbook as presentation state, not as an implicit mutation target.
- Say a change is saved only when the tool result confirms the canonical Shortcut workbook and durable version. If saving fails, state that the latest change is not durable and offer the tool's retry path.
- Export creates a copy. It is never a substitute for saving the canonical workbook.
- Preserve unsupported workbook objects when the tool reports preserve-only support. Stop before a mutation that would silently remove or corrupt them.
