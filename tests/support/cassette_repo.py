"""Committed repo snapshot for deterministic planner cassette tests.

Cassette replay and message-hash guardrails use this tree — not the mutable
``fixtures/sample-app/`` checkout where developers configure live LLM endpoints
and API keys.
"""

from __future__ import annotations

from pathlib import Path

from finalstrike.config.context import RepoContext, load_repo_context

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
CASSETTE_SMOKE_REPO = WORKSPACE_ROOT / "tests" / "fixtures" / "cassette-smoke-v1"
CASSETTE_ACCEPTANCE_SMOKE = CASSETTE_SMOKE_REPO / "acceptance-smoke.md"


def load_cassette_smoke_context(
    *,
    inject_secrets: bool = False,
) -> RepoContext:
    """Load the committed cassette fixture repo (stable planner inputs)."""
    return load_repo_context(
        CASSETTE_SMOKE_REPO,
        acceptance_path=CASSETTE_ACCEPTANCE_SMOKE,
        inject_secrets=inject_secrets,
    )
