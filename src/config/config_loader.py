"""Read a JSON game configuration with line comments and deferred notices."""

import atexit
import json
import sys
from pathlib import Path
from typing import Any


_NOTICES: list[str] = []


def _print_notices() -> None:
    """Print deferred configuration notices when the program exits."""
    if not _NOTICES:
        return
    print("\nConfiguration notices:", file=sys.stderr)
    for notice in _NOTICES:
        print(notice, file=sys.stderr)
    _NOTICES.clear()


def queue_config_notice(message: str) -> None:
    """Queue a configuration notice for normal interpreter shutdown."""
    if message not in _NOTICES:
        _NOTICES.append(message)


atexit.register(_print_notices)


def _remove_comments(source: str) -> tuple[str, list[int]]:
    """Remove # and // comments outside strings, preserving line numbers."""
    cleaned: list[str] = []
    lines: list[int] = []
    in_string = False
    escaped = False
    for number, line in enumerate(source.splitlines(keepends=True), 1):
        for index, character in enumerate(line):
            if in_string:
                if escaped:
                    escaped = False
                elif character == "\\":
                    escaped = True
                elif character == '"':
                    in_string = False
            elif character == '"':
                in_string = True
            elif character == "#" or line[index:index + 2] == "//":
                ending = "\n" if line.endswith("\n") else ""
                cleaned.append(line[:index] + ending)
                lines.append(number)
                break
        else:
            cleaned.append(line)
    return "".join(cleaned), lines


class ConfigError(ValueError):
    """Report a configuration read error that the entry point can display."""


def _reject_constant(value: str) -> None:
    """Reject non-standard JSON numeric constants such as NaN."""
    raise ValueError(f"Non-standard JSON constant: {value}")


def load_config(file_path: str) -> dict[str, Any]:
    """Read raw settings without validating individual game parameters.

    Ignore full-line and inline # or // comments outside strings. Preserve
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

    cleaned, comment_lines = _remove_comments(source)
    if comment_lines:
        locations = ", ".join(str(number) for number in comment_lines)
        queue_config_notice(
            f"Info: '{path}': ignored comments on lines {locations}; "
            "the remaining configuration was used."
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
