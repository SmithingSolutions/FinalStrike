"""Pre-flight checks for development and upcoming phases."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from finalstrike.fixture_capabilities import (
    count_planned_items,
    default_capabilities_path,
    load_capabilities,
)
from finalstrike.computer_use.browser import browser_available, browser_check_detail
from finalstrike.config.loader import load_config
from finalstrike.phase_status import (
    IMPLEMENTED_PHASES,
    STUB_MODULES,
    STUB_TEMPLATES,
    next_unimplemented_phases,
)


class CheckStatus(str, Enum):
    OK = "ok"
    WARN = "warn"
    FAIL = "fail"
    SKIP = "skip"


@dataclass(frozen=True)
class DoctorCheck:
    name: str
    status: CheckStatus
    detail: str
    phase: int | None = None


def run_doctor_checks(
    *,
    repo: Path | None = None,
) -> list[DoctorCheck]:
    """Run guardrail checks. ``repo`` enables fixture-specific validation."""
    checks: list[DoctorCheck] = []

    checks.append(
        DoctorCheck(
            name="Implemented phases",
            status=CheckStatus.OK,
            detail=f"P0–P{max(IMPLEMENTED_PHASES)} complete; next: P{next_unimplemented_phases()[0]}",
        )
    )

    stub_count = len(STUB_MODULES) + len(STUB_TEMPLATES)
    checks.append(
        DoctorCheck(
            name="Stub modules",
            status=CheckStatus.WARN,
            detail=f"{stub_count} scaffolded paths awaiting P{next_unimplemented_phases()[0]}–P10",
            phase=next_unimplemented_phases()[0],
        )
    )

    if shutil.which("pytest") is None:
        checks.append(
            DoctorCheck(
                name="pytest on PATH",
                status=CheckStatus.FAIL,
                detail="Activate .venv or prefix with .venv/bin/pytest",
            )
        )
    else:
        checks.append(
            DoctorCheck(
                name="pytest on PATH",
                status=CheckStatus.OK,
                detail=shutil.which("pytest") or "",
            )
        )

    if repo is None:
        checks.append(
            DoctorCheck(
                name="Fixture repo",
                status=CheckStatus.SKIP,
                detail="Pass --repo for fixture and secrets checks",
            )
        )
        checks.extend(_optional_phase_checks())
        return checks

    if not repo.is_dir():
        checks.append(
            DoctorCheck(
                name="Fixture repo",
                status=CheckStatus.FAIL,
                detail=f"Repo path does not exist: {repo}",
            )
        )
        return checks

    checks.extend(_fixture_checks(repo))
    checks.extend(_optional_phase_checks(repo))
    return checks


def _fixture_checks(repo: Path) -> list[DoctorCheck]:
    checks: list[DoctorCheck] = []

    config_path = repo / "finalstrike.yaml"
    if config_path.is_file():
        checks.append(
            DoctorCheck(
                name="finalstrike.yaml",
                status=CheckStatus.OK,
                detail=str(config_path),
            )
        )
    else:
        checks.append(
            DoctorCheck(
                name="finalstrike.yaml",
                status=CheckStatus.FAIL,
                detail=f"Missing {config_path}",
            )
        )

    secrets_path = repo / ".finalstrike" / "secrets.env"
    if secrets_path.is_file():
        checks.append(
            DoctorCheck(
                name="Secrets vault",
                status=CheckStatus.OK,
                detail=str(secrets_path),
            )
        )
    else:
        checks.append(
            DoctorCheck(
                name="Secrets vault",
                status=CheckStatus.FAIL,
                detail=(
                    f"Missing {secrets_path} "
                    "(OPENAI_API_KEY and SLACK_BOT_TOKEN for tests)"
                ),
            )
        )

    smoke = repo / "acceptance-smoke.md"
    full = repo / "acceptance-full.md"
    if smoke.is_file() and full.is_file():
        checks.append(
            DoctorCheck(
                name="Acceptance fixtures",
                status=CheckStatus.OK,
                detail="acceptance-smoke.md and acceptance-full.md present",
            )
        )
    else:
        checks.append(
            DoctorCheck(
                name="Acceptance fixtures",
                status=CheckStatus.FAIL,
                detail="Missing acceptance-smoke.md or acceptance-full.md",
            )
        )

    capabilities_path = default_capabilities_path(repo)
    try:
        capabilities = load_capabilities(capabilities_path)
    except (FileNotFoundError, ValueError) as exc:
        checks.append(
            DoctorCheck(
                name="capabilities.yaml",
                status=CheckStatus.FAIL,
                detail=str(exc),
            )
        )
        return checks

    planned_count = count_planned_items(capabilities)
    if planned_count:
        checks.append(
            DoctorCheck(
                name="Fixture planned work",
                status=CheckStatus.WARN,
                detail=(
                    f"{planned_count} planned item(s) in capabilities.yaml "
                    "(acceptance-full.md not fully implemented)"
                ),
                phase=6,
            )
        )
    else:
        checks.append(
            DoctorCheck(
                name="Fixture planned work",
                status=CheckStatus.OK,
                detail="No planned capabilities remain",
            )
        )

    try:
        config = load_config(repo)
    except (OSError, ValueError):
        config = None

    if config is not None and config.ui is not None:
        detail = browser_check_detail(config.ui.browser)
        checks.append(
            DoctorCheck(
                name="Chrome/Chromium (P6)",
                status=CheckStatus.OK
                if browser_available(config.ui.browser)
                else CheckStatus.SKIP,
                detail=detail,
                phase=6,
            )
        )

    return checks


def _optional_phase_checks(repo: Path | None = None) -> list[DoctorCheck]:
    from finalstrike.providers.live import assess_live_llm

    checks: list[DoctorCheck] = []

    if repo is not None:
        llm_status = assess_live_llm(repo)
        checks.append(
            DoctorCheck(
                name="Live LLM (P5)",
                status=CheckStatus.OK if llm_status.ready else CheckStatus.SKIP,
                detail=llm_status.detail,
                phase=5,
            )
        )
    else:
        checks.append(
            DoctorCheck(
                name="Live LLM (P5)",
                status=CheckStatus.SKIP,
                detail="Pass --repo to check configured llm.base_url",
                phase=5,
            )
        )

    for binary, phase, label in (
        ("ffmpeg", 7, "FFmpeg desktop recording"),
        ("xdotool", 6, "Linux input (X11)"),
        ("ydotool", 6, "Linux input (Wayland)"),
    ):
        path = shutil.which(binary)
        if path:
            checks.append(
                DoctorCheck(
                    name=f"{binary} (P{phase})",
                    status=CheckStatus.OK,
                    detail=path,
                    phase=phase,
                )
            )
        else:
            checks.append(
                DoctorCheck(
                    name=f"{binary} (P{phase})",
                    status=CheckStatus.SKIP,
                    detail=f"Not found — required for {label}",
                    phase=phase,
                )
            )

    return checks


def doctor_exit_code(checks: list[DoctorCheck]) -> int:
    if any(check.status == CheckStatus.FAIL for check in checks):
        return 1
    return 0
