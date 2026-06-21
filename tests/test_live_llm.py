"""Tests for live LLM readiness assessment."""

from __future__ import annotations

from pathlib import Path

import httpx
import pytest

from finalstrike.providers.live import assess_live_llm


def test_assess_live_llm_unreachable_local_endpoint(tmp_path: Path) -> None:
    (tmp_path / "finalstrike.yaml").write_text(
        """
version: "1"
project:
  name: ollama-probe
llm:
  provider: openai_compat
  base_url: http://localhost:11434/v1
  model: llama3
""".strip()
        + "\n",
        encoding="utf-8",
    )
    status = assess_live_llm(tmp_path)
    assert not status.ready
    assert status.base_url == "http://localhost:11434/v1"
    assert status.model == "llama3"
    assert "Cannot reach" in status.detail or "returned HTTP" in status.detail


def test_assess_live_llm_missing_api_key_for_remote(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    (tmp_path / "finalstrike.yaml").write_text(
        """
version: "1"
project:
  name: test-app
llm:
  provider: openai_compat
  base_url: https://api.example.com/v1
  model: gpt-4o
secrets:
  file: .finalstrike/secrets.env
""".strip()
        + "\n",
        encoding="utf-8",
    )
    status = assess_live_llm(tmp_path)
    assert not status.ready
    assert "OPENAI_API_KEY" in status.detail


def test_assess_live_llm_ready_when_models_endpoint_ok(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    secrets_dir = tmp_path / ".finalstrike"
    secrets_dir.mkdir()
    (secrets_dir / "secrets.env").write_text(
        "OPENAI_API_KEY=test-key\n",
        encoding="utf-8",
    )
    (tmp_path / "finalstrike.yaml").write_text(
        """
version: "1"
project:
  name: test-app
llm:
  provider: openai_compat
  base_url: https://api.example.com/v1
  model: gpt-4o
secrets:
  file: .finalstrike/secrets.env
""".strip()
        + "\n",
        encoding="utf-8",
    )

    class FakeResponse:
        status_code = 200

    class FakeClient:
        def __init__(self, *args, **kwargs) -> None:
            del args, kwargs

        def __enter__(self):
            return self

        def __exit__(self, *args) -> None:
            del args

        def get(self, url: str, *, headers: dict[str, str]) -> FakeResponse:
            assert url == "https://api.example.com/v1/models"
            assert headers["Authorization"] == "Bearer test-key"
            return FakeResponse()

    monkeypatch.setattr(httpx, "Client", FakeClient)
    status = assess_live_llm(tmp_path)
    assert status.ready
    assert "reachable" in status.detail


def test_assess_live_llm_rejects_invalid_api_key(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    secrets_dir = tmp_path / ".finalstrike"
    secrets_dir.mkdir()
    (secrets_dir / "secrets.env").write_text(
        "OPENAI_API_KEY=bad-key\n",
        encoding="utf-8",
    )
    (tmp_path / "finalstrike.yaml").write_text(
        """
version: "1"
project:
  name: test-app
llm:
  provider: openai_compat
  base_url: https://api.example.com/v1
  model: gpt-4o
secrets:
  file: .finalstrike/secrets.env
""".strip()
        + "\n",
        encoding="utf-8",
    )

    class FakeResponse:
        status_code = 401

    class FakeClient:
        def __init__(self, *args, **kwargs) -> None:
            del args, kwargs

        def __enter__(self):
            return self

        def __exit__(self, *args) -> None:
            del args

        def get(self, url: str, *, headers: dict[str, str]) -> FakeResponse:
            del url, headers
            return FakeResponse()

    monkeypatch.setattr(httpx, "Client", FakeClient)
    status = assess_live_llm(tmp_path)
    assert not status.ready
    assert "rejected" in status.detail
