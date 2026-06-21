"""Resolve computer-use configuration from repo context."""

from __future__ import annotations

from finalstrike.config.models import ComputerUseConfig, FinalStrikeConfig, LLMConfig


def resolve_computer_use_llm(config: FinalStrikeConfig) -> LLMConfig:
    """Return the LLM config for computer-use, falling back to the planner ``llm`` block."""
    block: ComputerUseConfig | None = config.computer_use
    if block is not None and block.llm is not None:
        return block.llm
    return config.llm
