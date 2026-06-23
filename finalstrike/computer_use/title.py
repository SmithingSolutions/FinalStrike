"""Page title helpers for computer-use verification."""

from __future__ import annotations

import re
import time

from finalstrike.computer_use.platform.a11y import AccessibilityDriver

_TITLE_RE = re.compile(
    r'(?:page\s+)?title\s+is\s+["\']([^"\']+)["\']',
    re.IGNORECASE,
)


def expected_title_from_instruction(instruction: str) -> str | None:
    """Extract a quoted title from instructions like ``verify the page title is "Foo"``."""
    match = _TITLE_RE.search(instruction)
    if match is None:
        return None
    return match.group(1).strip()


def window_list_includes_title(windows: list[str], expected: str) -> bool:
    """Return whether any visible window title contains ``expected``."""
    needle = expected.casefold()
    return any(needle in window.casefold() for window in windows)


def wait_for_window_title(
    a11y: AccessibilityDriver,
    expected: str,
    *,
    timeout: float = 10.0,
    poll_interval: float = 0.25,
) -> bool:
    """Poll visible window titles until ``expected`` appears or ``timeout`` elapses."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if window_list_includes_title(a11y.capture().windows, expected):
            return True
        time.sleep(poll_interval)
    return False
