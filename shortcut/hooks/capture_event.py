"""Consent-scoped local capture spike for documented Codex hook events.

This script deliberately performs no network I/O and never reads transcript_path.
It writes a bounded JSONL outbox under PLUGIN_DATA only after the user activates
Shortcut in the current Codex session. Phase 3 replaces the local spike outbox
with authenticated synchronization while preserving the event contract.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
MAX_STDIN_BYTES = 512 * 1024
MAX_TEXT_BYTES = 64 * 1024
MAX_TOOL_VALUE_BYTES = 16 * 1024
MAX_OUTBOX_BYTES = 5 * 1024 * 1024
ACTIVATION_PREFIX = "activate shortcut:"
DEACTIVATION_RE = re.compile(
    r"^\s*(?:\$shortcut\s+deactivate|deactivate shortcut)\b", re.IGNORECASE
)
INVOCATION_RE = re.compile(r"^\s*(?:\$shortcut\b|use shortcut\b)", re.IGNORECASE)
SENSITIVE_KEY_RE = re.compile(
    r"(?:authorization|cookie|password|secret|token|signed[_-]?url|credential|api[_-]?key)",
    re.IGNORECASE,
)


def _bounded_text(value: Any, max_bytes: int = MAX_TEXT_BYTES) -> str | None:
    if not isinstance(value, str):
        return None
    encoded = value.encode("utf-8", errors="replace")
    if len(encoded) <= max_bytes:
        return value
    suffix = b"\n[truncated]"
    return (encoded[: max_bytes - len(suffix)] + suffix).decode(
        "utf-8", errors="ignore"
    )


def _bounded_json(value: Any, max_bytes: int = MAX_TOOL_VALUE_BYTES) -> Any:
    def redact(candidate: Any) -> Any:
        if isinstance(candidate, dict):
            return {
                str(key): "[redacted]"
                if SENSITIVE_KEY_RE.search(str(key))
                else redact(item)
                for key, item in candidate.items()
            }
        if isinstance(candidate, list):
            return [redact(item) for item in candidate]
        if isinstance(candidate, str):
            return _bounded_text(candidate, max_bytes)
        if candidate is None or isinstance(candidate, (bool, int, float)):
            return candidate
        return str(candidate)

    redacted = redact(value)
    encoded = json.dumps(redacted, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )
    if len(encoded) <= max_bytes:
        return redacted
    return {"truncated": True, "byte_length": len(encoded)}


def _read_input() -> dict[str, Any]:
    raw = sys.stdin.buffer.read(MAX_STDIN_BYTES + 1)
    if len(raw) > MAX_STDIN_BYTES:
        raise ValueError("hook input exceeds limit")
    value = json.loads(raw.decode("utf-8"))
    if not isinstance(value, dict):
        raise TypeError("hook input must be an object")
    return value


def _data_root() -> Path:
    raw = os.environ.get("PLUGIN_DATA")
    if not raw:
        raise ValueError("PLUGIN_DATA is unavailable")
    root = Path(raw)
    root.mkdir(parents=True, exist_ok=True)
    return root


def _session_key(session_id: str) -> str:
    return hashlib.sha256(session_id.encode("utf-8")).hexdigest()


def _state_path(root: Path, session_id: str) -> Path:
    return root / "history-state" / f"{_session_key(session_id)}.json"


def _load_state(root: Path, session_id: str) -> dict[str, Any] | None:
    path = _state_path(root, session_id)
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None
    return value if isinstance(value, dict) and value.get("active") is True else None


def _write_state(root: Path, session_id: str, turn_id: str | None) -> None:
    path = _state_path(root, session_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    value = {
        "active": True,
        "schema_version": SCHEMA_VERSION,
        "session_id": session_id,
        "activation_turn_id": turn_id,
        "activated_at_ms": int(time.time() * 1000),
    }
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(value, separators=(",", ":")) + "\n", encoding="utf-8")
    os.replace(temp, path)


def _remove_state(root: Path, session_id: str) -> None:
    try:
        _state_path(root, session_id).unlink()
    except FileNotFoundError:
        pass


def _event_id(event: dict[str, Any]) -> str:
    identity = ":".join(
        str(event.get(key) or "")
        for key in ("session_id", "turn_id", "event_type", "tool_use_id")
    )
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()


def _append_event(root: Path, event: dict[str, Any]) -> None:
    event["schema_version"] = SCHEMA_VERSION
    event["captured_at_ms"] = int(time.time() * 1000)
    event["event_id"] = _event_id(event)
    payload = (
        json.dumps(event, separators=(",", ":"), ensure_ascii=False) + "\n"
    ).encode("utf-8")
    if len(payload) > MAX_TEXT_BYTES + MAX_TOOL_VALUE_BYTES * 2 + 4096:
        raise ValueError("normalized hook event exceeds limit")

    outbox_dir = root / "history-outbox"
    outbox_dir.mkdir(parents=True, exist_ok=True)
    path = outbox_dir / f"{_session_key(str(event['session_id']))}.jsonl"
    if path.exists() and path.stat().st_size + len(payload) > MAX_OUTBOX_BYTES:
        rotated = path.with_suffix(".jsonl.1")
        try:
            rotated.unlink()
        except FileNotFoundError:
            pass
        os.replace(path, rotated)
    descriptor = os.open(path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)
    try:
        os.write(descriptor, payload)
    finally:
        os.close(descriptor)


def _activation_block() -> dict[str, Any]:
    return {
        "decision": "block",
        "reason": (
            "Shortcut is not active for this task. If you continue, supported user prompts, "
            "final assistant responses, and Shortcut tool activity from activation onward will "
            "be sent to Shortcut and retained under Shortcut's production session policy. "
            "Earlier task history will not be captured. Re-submit the request beginning with "
            "'Activate Shortcut:' to consent and continue."
        ),
    }


def _base_event(data: dict[str, Any], event_type: str) -> dict[str, Any]:
    return {
        "event_type": event_type,
        "session_id": str(data["session_id"]),
        "turn_id": str(data["turn_id"]) if data.get("turn_id") is not None else None,
    }


def main() -> int:
    data = _read_input()
    session_id = data.get("session_id")
    hook_event = data.get("hook_event_name")
    if (
        not isinstance(session_id, str)
        or not session_id
        or not isinstance(hook_event, str)
    ):
        return 0

    root = _data_root()
    state = _load_state(root, session_id)

    if hook_event == "UserPromptSubmit":
        prompt = data.get("prompt")
        if not isinstance(prompt, str):
            return 0
        if DEACTIVATION_RE.search(prompt):
            _remove_state(root, session_id)
            print(
                json.dumps(
                    {"systemMessage": "Shortcut history capture is off for this task."}
                )
            )
            return 0
        if state is None:
            if prompt.strip().lower().startswith(ACTIVATION_PREFIX):
                _write_state(root, session_id, str(data.get("turn_id") or "") or None)
                state = _load_state(root, session_id)
            elif INVOCATION_RE.search(prompt):
                print(json.dumps(_activation_block()))
                return 0
            else:
                return 0
        event = _base_event(data, "user_prompt")
        event["text"] = _bounded_text(prompt)
        _append_event(root, event)
        return 0

    if state is None:
        return 0

    if hook_event == "Stop":
        event = _base_event(data, "assistant_response")
        event["text"] = _bounded_text(data.get("last_assistant_message"))
        _append_event(root, event)
    elif hook_event == "PostToolUse":
        tool_name = data.get("tool_name")
        if not isinstance(tool_name, str) or not tool_name.startswith(
            "mcp__shortcut__"
        ):
            return 0
        event = _base_event(data, "shortcut_tool_result")
        event["tool_name"] = tool_name
        event["tool_use_id"] = str(data.get("tool_use_id") or "") or None
        event["tool_input"] = _bounded_json(data.get("tool_input"))
        event["tool_response"] = _bounded_json(data.get("tool_response"))
        _append_event(root, event)
    elif hook_event == "SessionStart":
        event = _base_event(data, "session_start")
        event["source"] = _bounded_text(data.get("source"), 128)
        _append_event(root, event)
    elif hook_event == "SessionEnd":
        event = _base_event(data, "session_end")
        event["reason"] = _bounded_text(data.get("reason"), 128)
        _append_event(root, event)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        # History capture must never block workbook work because of a local outbox failure.
        raise SystemExit(0)
