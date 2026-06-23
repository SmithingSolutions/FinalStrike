"""Self-contained test repos — no dependency on gitignored developer files."""

from __future__ import annotations

import shutil
from pathlib import Path

from tests.support.cassette_repo import CASSETTE_ACCEPTANCE_SMOKE, CASSETTE_SMOKE_REPO

CASSETTE_SECRETS_ENV = """\
OPENAI_API_KEY=fixture-test-key-not-real
SLACK_BOT_TOKEN=fixture-slack-token
"""


def materialize_cassette_repo(
    tmp_path: Path,
    *,
    local_yaml: str | None = None,
    secrets_env: str = CASSETTE_SECRETS_ENV,
) -> Path:
    """Copy the committed cassette tree into ``tmp_path`` with test secrets.

    Optional ``local_yaml`` simulates a developer's gitignored
    ``finalstrike.local.yaml`` without touching ``fixtures/sample-app``.
    """
    repo = tmp_path / "repo"
    shutil.copytree(
        CASSETTE_SMOKE_REPO,
        repo,
        ignore=shutil.ignore_patterns("finalstrike.local.yaml"),
        dirs_exist_ok=True,
    )
    secrets_dir = repo / ".finalstrike"
    secrets_dir.mkdir(parents=True, exist_ok=True)
    (secrets_dir / "secrets.env").write_text(secrets_env, encoding="utf-8")
    if local_yaml is not None:
        (repo / "finalstrike.local.yaml").write_text(local_yaml, encoding="utf-8")
    return repo


def cassette_acceptance_path(repo: Path) -> Path:
    """Acceptance file inside a materialized cassette repo."""
    return repo / CASSETTE_ACCEPTANCE_SMOKE.name
