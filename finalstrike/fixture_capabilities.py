"""Load and validate fixture capabilities.yaml."""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field


class APICapability(BaseModel):
    model_config = ConfigDict(extra="forbid")

    method: str
    path: str
    expect_status: int


class UICapability(BaseModel):
    model_config = ConfigDict(extra="forbid")

    route: str | None = None
    title: str | None = None
    description: str | None = None
    action: str | None = None


class TerminalCapability(BaseModel):
    model_config = ConfigDict(extra="forbid")

    command: str


class CapabilityLayers(BaseModel):
    model_config = ConfigDict(extra="forbid")

    api: list[APICapability] = Field(default_factory=list)
    ui: list[UICapability] = Field(default_factory=list)
    terminal: list[TerminalCapability] = Field(default_factory=list)


class FixtureCapabilities(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: str
    implemented: CapabilityLayers = Field(default_factory=CapabilityLayers)
    planned: CapabilityLayers = Field(default_factory=CapabilityLayers)


def load_capabilities(path: Path) -> FixtureCapabilities:
    """Load capabilities.yaml from a fixture repo."""
    if not path.is_file():
        raise FileNotFoundError(f"capabilities manifest not found: {path}")
    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"capabilities manifest must be a mapping: {path}")
    return FixtureCapabilities.model_validate(data)


def default_capabilities_path(repo: Path) -> Path:
    return repo / "capabilities.yaml"


def count_planned_items(capabilities: FixtureCapabilities) -> int:
    layers = capabilities.planned
    return len(layers.api) + len(layers.ui) + len(layers.terminal)
