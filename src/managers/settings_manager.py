"""Store and load the game settings."""

import json
from pathlib import Path

SETTINGS_FILE = Path("data/settings.json")
WORLDS = ("ice", "cosmic")

DEFAULTS: dict = {
    "world": "ice",
    "music": True,
    "sfx": True,
    "fullscreen": True,
}


def load_settings() -> dict:
    """Return the saved settings, using defaults for anything missing."""
    settings = dict(DEFAULTS)

    try:
        data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return settings

    if not isinstance(data, dict):
        return settings

    if data.get("world") in WORLDS:
        settings["world"] = data["world"]

    for key in ("music", "sfx", "fullscreen"):
        if isinstance(data.get(key), bool):
            settings[key] = data[key]

    return settings


def save_settings(settings: dict) -> None:
    """Write the settings to disk."""
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS_FILE.write_text(
        json.dumps(settings, indent=2),
        encoding="utf-8",
    )