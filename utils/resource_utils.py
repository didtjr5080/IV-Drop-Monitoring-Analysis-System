from __future__ import annotations

import sys
from pathlib import Path


def get_base_path() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return Path(__file__).resolve().parents[1]


def resolve_asset(relative_path: str) -> str:
    base = get_base_path()
    return str(base / relative_path)
