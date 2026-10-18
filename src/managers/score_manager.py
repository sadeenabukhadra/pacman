"""Validate and persist the ten best named scores."""

import json
import os
from pathlib import Path
import tempfile

SCORE_FILE = Path("high_scor.json")
MAX_SCORES = 10


def configure_scores(filename: str) -> None:
    """Use the score filename selected by the game configuration."""
    global SCORE_FILE
    SCORE_FILE = Path(filename)


def valid_name(name: str) -> bool:
    """Accept one to ten alphanumeric characters or spaces, not blank."""
    return bool(name.strip()) and len(name) <= 10 and all(
        char.isalnum() or char == " " for char in name
    )


def load_scores() -> list[dict[str, int | str]]:
    """Read valid entries, tolerating missing or malformed files."""
    try:
        data = json.loads(SCORE_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    if not isinstance(data, list):
        return []
    scores: list[dict[str, int | str]] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        name, score = item.get("name"), item.get("score")
        if (
            isinstance(name, str) and valid_name(name)
            and type(score) is int and score >= 0
        ):
            scores.append({"name": name.strip(), "score": score})
    scores.sort(key=lambda entry: int(entry["score"]), reverse=True)
    return scores[:MAX_SCORES]


def save_scores(scores: list[dict[str, int | str]]) -> None:
    """Atomically save scores; let the UI report filesystem errors."""
    SCORE_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=SCORE_FILE.parent,
            prefix=".scores-", suffix=".tmp", delete=False,
        ) as stream:
            temporary = stream.name
            json.dump(scores[:MAX_SCORES], stream, indent=4)
        os.replace(temporary, SCORE_FILE)
    finally:
        if temporary is not None and os.path.exists(temporary):
            os.unlink(temporary)


def is_high_score(score: int) -> bool:
    """Report whether a non-negative integer qualifies for the table."""
    if type(score) is not int or score < 0:
        return False
    scores = load_scores()
    return len(scores) < MAX_SCORES or score > int(scores[-1]["score"])


def add_score(name: str, score: int) -> None:
    """Validate a completed run and preserve the top ten entries."""
    if not valid_name(name):
        raise ValueError("Enter 1-10 letters, numbers or spaces.")
    if type(score) is not int or score < 0:
        raise ValueError("The score must be a non-negative integer.")
    scores = load_scores()
    scores.append({"name": name.strip(), "score": score})
    scores.sort(key=lambda entry: int(entry["score"]), reverse=True)
    save_scores(scores)
