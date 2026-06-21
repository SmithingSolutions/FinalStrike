"""Launch Google Chrome or Chromium for computer-use scenarios."""

from __future__ import annotations

import shutil
import subprocess
import time

from finalstrike.config.models import BrowserKind


_CHROME_PREFERRED = (
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
)

_CHROMIUM_PREFERRED = (
    "chromium",
    "chromium-browser",
    "google-chrome",
    "google-chrome-stable",
)


class BrowserLaunchError(RuntimeError):
    """Raised when Chrome/Chromium cannot be launched."""


def resolve_browser_binary(browser: BrowserKind) -> str:
    """Resolve a Chrome or Chromium binary path (required for computer-use)."""
    candidates = (
        _CHROME_PREFERRED if browser == BrowserKind.CHROME else _CHROMIUM_PREFERRED
    )
    for name in candidates:
        path = shutil.which(name)
        if path:
            return path
    label = "Google Chrome" if browser == BrowserKind.CHROME else "Chromium/Chrome"
    raise BrowserLaunchError(
        f"{label} not found on PATH. Computer-use requires Google Chrome or Chromium. "
        f"Install one of: {', '.join(candidates)}"
    )


def launch_browser(
    url: str,
    *,
    browser: BrowserKind,
    extra_args: list[str] | None = None,
) -> subprocess.Popen[bytes]:
    """Open a new browser window at ``url``."""
    binary = resolve_browser_binary(browser)
    args = [
        binary,
        "--new-window",
        "--no-first-run",
        "--disable-infobars",
        * (extra_args or []),
        url,
    ]
    try:
        process = subprocess.Popen(
            args,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except OSError as exc:
        raise BrowserLaunchError(f"failed to launch {binary}: {exc}") from exc
    time.sleep(1.5)
    return process


def browser_available(browser: BrowserKind) -> bool:
    try:
        resolve_browser_binary(browser)
    except BrowserLaunchError:
        return False
    return True


def browser_check_detail(browser: BrowserKind) -> str:
    try:
        return resolve_browser_binary(browser)
    except BrowserLaunchError as exc:
        return str(exc)
