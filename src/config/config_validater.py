"""Validate raw game settings and provide independent safe defaults."""

from typing import Any, TypedDict

from .config_loader import queue_config_notice


class LevelConfig(TypedDict):
    """Describe one level in generator cell dimensions."""

    width: int
    height: int


class GameConfig(TypedDict):
    """Describe normalized settings passed to the game."""

    highscore_filename: str
    theme: str
    lives: int
    pacgum: int
    point_per_pacgum: int
    point_per_super_pacgum: int
    point_per_ghost: int
    seed: int
    level_max_time: int
    level: list[LevelConfig]


MIN_MAZE_SIZE = 3
MAX_MAZE_SIZE = 100
MIN_LEVELS = 10
MAX_LEVEL_TIME = 300

DEFAULT_CONFIG: GameConfig = {
    "highscore_filename": "highscore.json",
    "theme": "cosmic",
    "lives": 3,
    "pacgum": 42,
    "point_per_pacgum": 10,
    "point_per_super_pacgum": 50,
    "point_per_ghost": 200,
    "seed": 42,
    "level_max_time": 90,
    "level": [
        {"width": size, "height": size}
        for size in (14, 18, 22, 26, 30, 34, 38, 42, 46, 50)
    ],
}


def _warn(key: str, message: str) -> None:
    """Defer a readable warning until normal program exit."""
    queue_config_notice(f"Warning: '{key}': {message}")


def _integer(
    value: object,
    default: int,
    key: str,
    minimum: int,
    maximum: int | None = None,
) -> int:
    """Replace only an invalid integer field with its own default."""
    if not isinstance(value, int) or isinstance(value, bool):
        _warn(key, f"missing or not an integer; using {default}.")
        return default
    if maximum is not None and value > maximum:
        _warn(key, f"value {value} exceeds maximum {maximum}; "
              f"using default {default}.")
        return default
    if value < minimum:
        _warn(key, f"value {value} is out of range; using {default}.")
        return default
    return value


def _value(config: dict[str, Any], key: str, alias: str) -> object:
    """Prefer the canonical key, accepting a known legacy spelling."""
    if key in config:
        return config[key]
    if alias in config:
        _warn(alias, f"accepted as '{key}'; prefer the canonical spelling.")
        return config[alias]
    return None


def _filename(value: object) -> str:
    """Normalize a non-empty highscore path without opening it."""
    if isinstance(value, str) and value.strip() and "\x00" not in value:
        return value.strip()
    default = DEFAULT_CONFIG["highscore_filename"]
    _warn("highscore_filename", f"missing or invalid; using '{default}'.")
    return default


def _theme(value: object) -> str:
    """Accept either supported theme, ignoring case and outer spaces."""
    if isinstance(value, str):
        name = value.strip().lower()
        if name in ("ice", "cosmic"):
            return name
    default = DEFAULT_CONFIG["theme"]
    _warn("theme", f"missing or invalid; using '{default}'.")
    return default


def _copy_default_levels() -> list[LevelConfig]:
    """Return fresh level dictionaries to avoid sharing mutable defaults."""
    return [
        {"width": level["width"], "height": level["height"]}
        for level in DEFAULT_CONFIG["level"]
    ]


def _levels(value: object) -> list[LevelConfig]:
    """Validate dimensions and pad short level lists to ten levels.

    Generator dimensions are limited to 3..100 cells for this graphical
    implementation. Retain valid supplied levels when replacing bad ones.
    """
    defaults = _copy_default_levels()
    if not isinstance(value, list) or not value:
        _warn("level", "missing, empty or not a list; using default levels.")
        return defaults
    result: list[LevelConfig] = []
    for index, item in enumerate(value):
        fallback = defaults[min(index, len(defaults) - 1)]
        if not isinstance(item, dict):
            _warn(f"level[{index}]", "not an object; using a default level.")
            result.append({
                "width": fallback["width"], "height": fallback["height"],
            })
            continue
        result.append({
            "width": _integer(
                item.get("width"), fallback["width"],
                f"level[{index}].width", MIN_MAZE_SIZE, MAX_MAZE_SIZE,
            ),
            "height": _integer(
                item.get("height"), fallback["height"],
                f"level[{index}].height", MIN_MAZE_SIZE, MAX_MAZE_SIZE,
            ),
        })
    if len(result) < MIN_LEVELS:
        _warn("level", "at least ten levels required; adding default levels.")
        result.extend(defaults[len(result):])
    return result


def config_validator(config: dict[str, Any]) -> GameConfig:
    """Return complete validated settings, ignoring unknown keys.

    Accept the user's existing singular 'point_per_*' keys. Plural
    'points_per_*' keys and the old 'highscor_filename' spelling are
    accepted as aliases, with canonical keys taking precedence.

    Args:
        config: Raw JSON object returned by load_config.

    Returns:
        Fully populated settings with independent level dictionaries.
    """
    return {
        "highscore_filename": _filename(_value(
            config, "highscore_filename", "highscor_filename",
        )),
        "theme": _theme(config.get("theme")),
        "lives": _integer(
            config.get("lives"), DEFAULT_CONFIG["lives"], "lives", 1,
        ),
        "pacgum": _integer(
            config.get("pacgum"), DEFAULT_CONFIG["pacgum"], "pacgum", 0,
        ),
        "point_per_pacgum": _integer(
            _value(config, "point_per_pacgum", "points_per_pacgum"),
            DEFAULT_CONFIG["point_per_pacgum"], "point_per_pacgum", 0,
        ),
        "point_per_super_pacgum": _integer(
            _value(
                config, "point_per_super_pacgum", "points_per_super_pacgum",
            ),
            DEFAULT_CONFIG["point_per_super_pacgum"],
            "point_per_super_pacgum", 0,
        ),
        "point_per_ghost": _integer(
            _value(config, "point_per_ghost", "points_per_ghost"),
            DEFAULT_CONFIG["point_per_ghost"], "point_per_ghost", 0,
        ),
        # The supplied generator treats seed <= 0 as nondeterministic.
        "seed": _integer(
            config.get("seed"), DEFAULT_CONFIG["seed"], "seed", 1,
        ),
        "level_max_time": _integer(
            config.get("level_max_time"), DEFAULT_CONFIG["level_max_time"],
            "level_max_time", 1, MAX_LEVEL_TIME,
        ),
        "level": _levels(config.get("level")),
    }
