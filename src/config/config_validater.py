from typing import Any


DEFAULT_CONFIG: dict[str, Any] = {
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
        {"width": 14, "height": 14},
        {"width": 18, "height": 18},
        {"width": 22, "height": 22},
        {"width": 26, "height": 26},
        {"width": 30, "height": 30},
        {"width": 34, "height": 34},
        {"width": 38, "height": 38},
        {"width": 42, "height": 42},
        {"width": 46, "height": 46},
        {"width": 50, "height": 50},
    ],
}


def config_validator(config: dict[str, Any]) -> dict[str, Any]:
    validated_config: dict[str, Any] = {}

    if (
        "highscore_filename" not in config
        or not isinstance(config["highscore_filename"], str)
    ):
        print(
            "Warning: invalid or missing 'highscore_filename'. "
            f"Using default value: "
            f"{DEFAULT_CONFIG['highscore_filename']}"
        )
        validated_config["highscore_filename"] = (
            DEFAULT_CONFIG["highscore_filename"]
        )
    else:
        validated_config["highscore_filename"] = _valid_string(
            config["highscore_filename"],
            DEFAULT_CONFIG["highscore_filename"],
            "highscore_filename",
        )

    if (
        "theme" not in config
        or not isinstance(config["theme"], str)
    ):
        print(
            "Warning: invalid or missing 'theme'. "
            f"Using default value: {DEFAULT_CONFIG['theme']}"
        )
        validated_config["theme"] = DEFAULT_CONFIG["theme"]
    else:
        validated_config["theme"] = _valid_theme(
            config["theme"],
            DEFAULT_CONFIG["theme"],
        )

    if "lives" not in config or type(config["lives"]) is not int:
        print(
            "Warning: invalid or missing 'lives'. "
            f"Using default value: {DEFAULT_CONFIG['lives']}"
        )
        validated_config["lives"] = DEFAULT_CONFIG["lives"]
    else:
        validated_config["lives"] = _valid_integer(
            config["lives"],
            DEFAULT_CONFIG["lives"],
            "lives",
            min_value=1,
        )

    if "pacgum" not in config or type(config["pacgum"]) is not int:
        print(
            "Warning: invalid or missing 'pacgum'. "
            f"Using default value: {DEFAULT_CONFIG['pacgum']}"
        )
        validated_config["pacgum"] = DEFAULT_CONFIG["pacgum"]
    else:
        validated_config["pacgum"] = _valid_integer(
            config["pacgum"],
            DEFAULT_CONFIG["pacgum"],
            "pacgum",
            min_value=0,
        )

    if (
        "point_per_pacgum" not in config
        or type(config["point_per_pacgum"]) is not int
    ):
        print(
            "Warning: invalid or missing 'point_per_pacgum'. "
            f"Using default value: {DEFAULT_CONFIG['point_per_pacgum']}"
        )
        validated_config["point_per_pacgum"] = (
            DEFAULT_CONFIG["point_per_pacgum"]
        )
    else:
        validated_config["point_per_pacgum"] = _valid_integer(
            config["point_per_pacgum"],
            DEFAULT_CONFIG["point_per_pacgum"],
            "point_per_pacgum",
            min_value=0,
        )

    if (
        "point_per_super_pacgum" not in config
        or type(config["point_per_super_pacgum"]) is not int
    ):
        print(
            "Warning: invalid or missing 'point_per_super_pacgum'. "
            f"Using default value: "
            f"{DEFAULT_CONFIG['point_per_super_pacgum']}"
        )
        validated_config["point_per_super_pacgum"] = (
            DEFAULT_CONFIG["point_per_super_pacgum"]
        )
    else:
        validated_config["point_per_super_pacgum"] = _valid_integer(
            config["point_per_super_pacgum"],
            DEFAULT_CONFIG["point_per_super_pacgum"],
            "point_per_super_pacgum",
            min_value=0,
        )

    if (
        "point_per_ghost" not in config
        or type(config["point_per_ghost"]) is not int
    ):
        print(
            "Warning: invalid or missing 'point_per_ghost'. "
            f"Using default value: {DEFAULT_CONFIG['point_per_ghost']}"
        )
        validated_config["point_per_ghost"] = (
            DEFAULT_CONFIG["point_per_ghost"]
        )
    else:
        validated_config["point_per_ghost"] = _valid_integer(
            config["point_per_ghost"],
            DEFAULT_CONFIG["point_per_ghost"],
            "point_per_ghost",
            min_value=0,
        )

    if "seed" not in config or type(config["seed"]) is not int:
        print(
            "Warning: invalid or missing 'seed'. "
            f"Using default value: {DEFAULT_CONFIG['seed']}"
        )
        validated_config["seed"] = DEFAULT_CONFIG["seed"]
    else:
        validated_config["seed"] = _valid_integer(
            config["seed"],
            DEFAULT_CONFIG["seed"],
            "seed",
            min_value=0,
        )

    if (
        "level_max_time" not in config
        or type(config["level_max_time"]) is not int
    ):
        print(
            "Warning: invalid or missing 'level_max_time'. "
            f"Using default value: {DEFAULT_CONFIG['level_max_time']}"
        )
        validated_config["level_max_time"] = (
            DEFAULT_CONFIG["level_max_time"]
        )
    else:
        validated_config["level_max_time"] = _valid_integer(
            config["level_max_time"],
            DEFAULT_CONFIG["level_max_time"],
            "level_max_time",
            min_value=1,
        )
        if (
            "level" not in config
            or not isinstance(config["level"], list)
        ):
            print(
                "Warning: invalid or missing 'level'. "
                "Using default levels."
            )
            validated_config["level"] = DEFAULT_CONFIG["level"]
        else:
            validated_config["level"] = _valid_levels(
                config["level"],
                DEFAULT_CONFIG["level"],
            )

        return validated_config


def _valid_integer(
    value: int,
    default: int,
    key: str,
    min_value: int = 0,
) -> int:
    if value < min_value:
        print(
            f"Warning: invalid value for '{key}': {value}. "
            f"Using default value: {default}"
        )
        return default

    return value


def _valid_string(
    value: str,
    default: str,
    key: str,
) -> str:
    if not value.strip():
        print(
            f"Warning: invalid value for '{key}'. "
            f"Using default value: {default}"
        )
        return default

    return value


def _valid_theme(value: str, default: str) -> str:
    valid_themes = ("cosmic", "ice")

    if value not in valid_themes:
        print(
            f"Warning: invalid theme '{value}'. "
            f"Using default value: {default}"
        )
        return default

    return value


def _valid_levels(
    levels: list[Any],
    default: list[dict[str, int]],
) -> list[dict[str, int]]:
    if len(levels) < 10:
        print(
            "Warning: at least 10 levels are required. "
            "Using default levels."
        )
        return default

    validated_levels: list[dict[str, int]] = []

    for index, level in enumerate(levels):
        if not isinstance(level, dict):
            print(
                f"Warning: level {index + 1} is invalid. "
                "Using default levels."
            )
            return default

        if "width" not in level or "height" not in level:
            print(
                f"Warning: width or height is missing "
                f"in level {index + 1}. "
                "Using default levels."
            )
            return default

        width = level["width"]
        height = level["height"]

        if type(width) is not int or type(height) is not int:
            print(
                f"Warning: width and height in level "
                f"{index + 1} must be integers. "
                "Using default levels."
            )
            return default

        if width <= 0 or height <= 0:
            print(
                f"Warning: invalid width or height "
                f"in level {index + 1}. "
                "Using default levels."
            )
            return default

        validated_levels.append(
            {
                "width": width,
                "height": height,
            }
        )

    return validated_levels
