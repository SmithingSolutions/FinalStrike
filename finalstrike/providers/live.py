"""Assess whether a repo's configured LLM endpoint is ready for live calls."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import httpx
from pydantic import ValidationError

from finalstrike.config.loader import load_config
from finalstrike.config.secrets import load_secrets
from finalstrike.providers.openai_compat import LLMProviderError, resolve_api_key


@dataclass(frozen=True)
class LiveLLMStatus:
    ready: bool
    detail: str
    base_url: str | None = None
    model: str | None = None


def assess_live_llm(repo: Path) -> LiveLLMStatus:
    """Return whether ``finalstrike.yaml`` + secrets can reach the configured LLM."""
    repo = repo.resolve()
    try:
        config = load_config(repo)
    except (FileNotFoundError, ValueError, ValidationError) as exc:
        return LiveLLMStatus(ready=False, detail=f"Cannot load config: {exc}")

    llm = config.llm
    secrets, _ = load_secrets(repo, config.secrets.file)

    try:
        api_key = resolve_api_key(secrets, base_url=llm.base_url)
    except LLMProviderError as exc:
        return LiveLLMStatus(
            ready=False,
            detail=str(exc),
            base_url=llm.base_url,
            model=llm.model,
        )

    models_url = f"{llm.base_url.rstrip('/')}/models"
    try:
        with httpx.Client(timeout=2.0) as client:
            response = client.get(
                models_url,
                headers={"Authorization": f"Bearer {api_key}"},
            )
    except httpx.HTTPError as exc:
        return LiveLLMStatus(
            ready=False,
            detail=f"Cannot reach {llm.base_url}: {exc}",
            base_url=llm.base_url,
            model=llm.model,
        )

    if response.status_code == 200:
        return LiveLLMStatus(
            ready=True,
            detail=f"{llm.base_url} ({llm.model}) reachable",
            base_url=llm.base_url,
            model=llm.model,
        )
    if response.status_code == 401:
        return LiveLLMStatus(
            ready=False,
            detail=f"OPENAI_API_KEY rejected by {llm.base_url}",
            base_url=llm.base_url,
            model=llm.model,
        )
    return LiveLLMStatus(
        ready=False,
        detail=f"{models_url} returned HTTP {response.status_code}",
        base_url=llm.base_url,
        model=llm.model,
    )
