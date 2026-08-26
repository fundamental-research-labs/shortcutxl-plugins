"""Behavior tests for the consent-scoped history capture spike."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "hooks" / "capture_event.py"


def run_hook(data_root: Path, payload: dict) -> tuple[int, dict | None]:
    result = subprocess.run(
        ["python3", str(HOOK)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        env={**os.environ, "PLUGIN_DATA": str(data_root)},
        check=False,
    )
    output = json.loads(result.stdout) if result.stdout.strip() else None
    return result.returncode, output


def outbox_events(data_root: Path) -> list[dict]:
    paths = list((data_root / "history-outbox").glob("*.jsonl"))
    if not paths:
        return []
    return [json.loads(line) for line in paths[0].read_text().splitlines() if line]


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        data_root = Path(temporary)
        base = {"session_id": "task-1", "turn_id": "turn-1"}

        code, output = run_hook(
            data_root,
            {
                **base,
                "hook_event_name": "UserPromptSubmit",
                "prompt": "Unrelated question",
            },
        )
        assert code == 0 and output is None and outbox_events(data_root) == []

        _, output = run_hook(
            data_root,
            {
                **base,
                "hook_event_name": "UserPromptSubmit",
                "prompt": "$shortcut inspect it",
            },
        )
        assert output and output["decision"] == "block"
        assert outbox_events(data_root) == []

        _, output = run_hook(
            data_root,
            {
                **base,
                "hook_event_name": "UserPromptSubmit",
                "prompt": "Activate Shortcut: inspect the workbook",
            },
        )
        assert output is None
        events = outbox_events(data_root)
        assert [event["event_type"] for event in events] == ["user_prompt"]
        assert events[0]["text"].startswith("Activate Shortcut:")

        run_hook(
            data_root,
            {
                **base,
                "hook_event_name": "Stop",
                "last_assistant_message": "Inspection complete.",
            },
        )
        run_hook(
            data_root,
            {
                **base,
                "hook_event_name": "PostToolUse",
                "tool_name": "mcp__shortcut__inspect_workbook",
                "tool_use_id": "tool-1",
                "tool_input": {"workbook_id": "file-1", "authorization": "secret"},
                "tool_response": {"ok": True, "token": "secret"},
            },
        )
        events = outbox_events(data_root)
        assert [event["event_type"] for event in events] == [
            "user_prompt",
            "assistant_response",
            "shortcut_tool_result",
        ]
        tool_event = events[-1]
        assert tool_event["tool_input"]["authorization"] == "[redacted]"
        assert tool_event["tool_response"]["token"] == "[redacted]"

        # A second process observes persisted activation state after restart.
        run_hook(
            data_root,
            {
                "session_id": "task-1",
                "turn_id": "turn-2",
                "hook_event_name": "UserPromptSubmit",
                "prompt": "Continue with the same workbook",
            },
        )
        assert outbox_events(data_root)[-1]["turn_id"] == "turn-2"

        # Repeated delivery has a stable id for server-side idempotency.
        duplicate_payload = {
            "session_id": "task-1",
            "turn_id": "turn-3",
            "hook_event_name": "Stop",
            "last_assistant_message": "Done",
        }
        run_hook(data_root, duplicate_payload)
        run_hook(data_root, duplicate_payload)
        final_events = outbox_events(data_root)
        assert final_events[-1]["event_id"] == final_events[-2]["event_id"]

        run_hook(
            data_root,
            {
                "session_id": "task-1",
                "turn_id": "turn-4",
                "hook_event_name": "UserPromptSubmit",
                "prompt": "$shortcut deactivate",
            },
        )
        before = len(outbox_events(data_root))
        run_hook(
            data_root,
            {
                "session_id": "task-1",
                "turn_id": "turn-4",
                "hook_event_name": "Stop",
                "last_assistant_message": "Not captured",
            },
        )
        assert len(outbox_events(data_root)) == before

    print("capture_event tests passed")


if __name__ == "__main__":
    main()
