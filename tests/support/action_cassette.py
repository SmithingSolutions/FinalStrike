"""Load committed computer-use action cassettes."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from finalstrike.computer_use.prompt import action_prompt_version


@dataclass(frozen=True)
class ActionCassetteMeta:
    id: str
    phase: int
    component: str
    instruction: str
    instruction_sha256: str
    prompt_version: str
    responses: int
    notes: str = ""


@dataclass(frozen=True)
class ActionCassette:
    root: Path
    meta: ActionCassetteMeta
    responses: list[str]
    canonical_result: dict[str, Any] | None = None


def recordings_root() -> Path:
    return Path(__file__).resolve().parents[1] / "llm_recordings"


def action_cassette_dir(cassette_id: str) -> Path:
    return recordings_root() / "computer_use" / cassette_id


def load_action_cassette(cassette_id: str) -> ActionCassette:
    root = action_cassette_dir(cassette_id)
    meta_path = root / "meta.yaml"
    responses_path = root / "responses.json"
    result_path = root / "result.canonical.json"

    for path in (meta_path, responses_path):
        if not path.is_file():
            raise FileNotFoundError(f"missing action cassette file: {path}")

    meta_data = yaml.safe_load(meta_path.read_text(encoding="utf-8"))
    if not isinstance(meta_data, dict):
        raise ValueError(f"invalid action cassette meta: {meta_path}")

    responses = json.loads(responses_path.read_text(encoding="utf-8"))
    if not isinstance(responses, list):
        raise ValueError(f"invalid responses JSON in {responses_path}")

    canonical_result = None
    if result_path.is_file():
        canonical_result = json.loads(result_path.read_text(encoding="utf-8"))

    return ActionCassette(
        root=root,
        meta=ActionCassetteMeta(**meta_data),
        responses=responses,
        canonical_result=canonical_result,
    )


def assert_action_cassette_current(cassette: ActionCassette) -> None:
    if cassette.meta.prompt_version != action_prompt_version():
        raise AssertionError(
            "computer-use prompt changed; refresh cassette "
            f"{cassette.meta.id!r}"
        )


DEFAULT_SMOKE_TITLE_CASSETTE_ID = "smoke-title-v1"
DEFAULT_FULL_TASKS_TITLE_CASSETTE_ID = "full-tasks-title-v1"
