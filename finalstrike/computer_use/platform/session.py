"""Detect Linux display session type for driver selection."""

from __future__ import annotations

import os
from enum import Enum


class SessionType(str, Enum):
    X11 = "x11"
    WAYLAND = "wayland"
    UNKNOWN = "unknown"


def detect_session_type() -> SessionType:
    """Best-effort session detection (X11 vs Wayland)."""
    session_type = os.environ.get("XDG_SESSION_TYPE", "").lower()
    if session_type == "wayland":
        return SessionType.WAYLAND
    if session_type == "x11":
        return SessionType.X11
    if os.environ.get("WAYLAND_DISPLAY"):
        return SessionType.WAYLAND
    if os.environ.get("DISPLAY"):
        return SessionType.X11
    return SessionType.UNKNOWN
