---
name: shortcut
description: Check whether Shortcut authentication and beta access are active in Codex. Use when the customer asks to connect Shortcut, verify the Shortcut connection, or check beta access.
---

# Shortcut

Use `shortcut_status` to verify the installed Shortcut connection and the signed-in account's beta access.

This Phase 0 package does not create, inspect, modify, save, show, or export workbooks. Never claim that workbook operations are available or that a workbook was changed. If the status call succeeds, report the returned connection state. If it fails, surface the error and say that Shortcut is not connected or the account is not enabled for the beta.
