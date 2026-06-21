"""Structured computer-use actions from the vision LLM."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator


class ActionPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal[
        "launch",
        "click",
        "type",
        "key",
        "scroll",
        "wait",
        "focus_window",
        "done",
    ]
    url: str | None = None
    x: int | None = None
    y: int | None = None
    text: str | None = None
    combo: str | None = None
    direction: Literal["up", "down", "left", "right"] | None = None
    amount: int | None = None
    seconds: float | None = None
    title: str | None = None
    success: bool | None = None
    message: str | None = None

    @model_validator(mode="after")
    def _validate_required_fields(self) -> ActionPayload:
        required: dict[str, tuple[str, ...]] = {
            "launch": ("url",),
            "click": ("x", "y"),
            "type": ("text",),
            "key": ("combo",),
            "scroll": ("direction",),
            "wait": ("seconds",),
            "focus_window": ("title",),
            "done": ("success",),
        }
        fields = required.get(self.type, ())
        missing = [name for name in fields if getattr(self, name) is None]
        if missing:
            raise ValueError(
                f"action type {self.type!r} requires field(s): {', '.join(missing)}"
            )
        return self


class ComputerActionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    thought: str = ""
    action: ActionPayload


def parse_action_response(raw: str) -> ComputerActionResponse:
    """Parse and validate LLM JSON output for a single action step."""
    try:
        return ComputerActionResponse.model_validate_json(raw)
    except ValidationError as exc:
        raise ValueError(f"invalid computer-use action JSON: {exc}") from exc


def action_summary(action: ActionPayload) -> str:
    """Human-readable action label for logs and RunResult steps."""
    if action.type == "launch":
        return f"launch({action.url})"
    if action.type == "click":
        return f"click({action.x}, {action.y})"
    if action.type == "type":
        text = action.text or ""
        preview = text if len(text) <= 40 else f"{text[:37]}..."
        return f"type({preview!r})"
    if action.type == "key":
        return f"key({action.combo})"
    if action.type == "scroll":
        return f"scroll({action.direction}, {action.amount})"
    if action.type == "wait":
        return f"wait({action.seconds}s)"
    if action.type == "focus_window":
        return f"focus_window({action.title!r})"
    if action.type == "done":
        return f"done(success={action.success})"
    return action.type


def extract_json_object(raw: str) -> dict[str, Any]:
    """Extract a JSON object from raw LLM text (tolerates markdown fences)."""
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("response does not contain a JSON object")
    import json

    parsed = json.loads(text[start : end + 1])
    if not isinstance(parsed, dict):
        raise ValueError("expected JSON object")
    return parsed
