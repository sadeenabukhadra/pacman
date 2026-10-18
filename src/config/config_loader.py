"""Read a JSON game configuration with full-line hash comments."""

import json
from pathlib import Path
from typing import Any


class ConfigError(ValueError):
    """Report a configuration read error that the entry point can display."""


def _reject_constant(value: str) -> None:
    """Reject non-standard JSON numeric constants such as NaN."""
    raise ValueError(f"Non-standard JSON constant: {value}")


def load_config(file_path: str) -> dict[str, Any]:
    """Read raw settings without validating individual game parameters.

    Ignore lines whose first non-whitespace character is '#'. Preserve
    line numbers for JSON error reporting. Hashes within strings remain
    unchanged. A UTF-8 byte order mark is accepted.

    Args:
        file_path: Path to the JSON configuration selected at launch.

    Returns:
        Raw JSON object for config_validator to normalize.

    Raises:
        ConfigError: If the file cannot be read, has a non-JSON extension,
            contains malformed JSON, or does not contain a JSON object.
    """
    path = Path(file_path)
    if path.suffix.lower() != ".json":
        raise ConfigError("Configuration must be a .json file.")
    try:
        source = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as error:
        raise ConfigError(
            f"Cannot read configuration '{path}': {error}"
        ) from error

    cleaned = "".join(
        "\n" if line.lstrip().startswith("#") else line
        for line in source.splitlines(keepends=True)
    )
    try:
        data: Any = json.loads(cleaned, parse_constant=_reject_constant)
    except json.JSONDecodeError as error:
        raise ConfigError(
            f"Invalid JSON in '{path}' at line {error.lineno}, "
            f"column {error.colno}: {error.msg}"
        ) from error
    except ValueError as error:
        raise ConfigError(f"Invalid JSON in '{path}': {error}") from error

    if not isinstance(data, dict):
        raise ConfigError("Configuration must contain a JSON object {...}.")
    result: dict[str, Any] = data
    return result
