from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


SETTINGS_PATH = Path("config/user_settings.json")


@dataclass
class UserSettings:
    theme_mode: str = "light"
    resolution: tuple[int, int] = (1600, 900)


def load_user_settings() -> UserSettings:
    if not SETTINGS_PATH.exists():
        return UserSettings()
    try:
        raw = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return UserSettings()

    theme = raw.get("theme_mode", "light")
    if theme not in {"light", "dark"}:
        theme = "light"

    resolution = raw.get("resolution", [1600, 900])
    if (
        isinstance(resolution, list)
        and len(resolution) == 2
        and all(isinstance(value, int) for value in resolution)
    ):
        res_tuple = (resolution[0], resolution[1])
    else:
        res_tuple = (1600, 900)

    return UserSettings(theme_mode=theme, resolution=res_tuple)


def save_user_settings(settings: UserSettings) -> None:
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "theme_mode": settings.theme_mode,
        "resolution": [settings.resolution[0], settings.resolution[1]],
    }
    SETTINGS_PATH.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")
