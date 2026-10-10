"""Store and load the high scores."""

import json
from pathlib import Path

SCORES_FILE = Path("data/high_scores.json")
MAX_SCORES = 10


def load_scores() -> list[dict]:
    """Return the saved scores, highest first."""
    try:
        data = json.loads(SCORES_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []

    if not isinstance(data, list):
        return []

    scores = [
        {"name": str(item["name"]), "score": int(item["score"])}
        for item in data
        if isinstance(item, dict) and "name" in item and "score" in item
    ]
    scores.sort(key=lambda item: item["score"], reverse=True)
    return scores[:MAX_SCORES]


def is_high_score(score: int) -> bool:
    """Check whether a score enters the top list."""
    scores = load_scores()
    return len(scores) < MAX_SCORES or score > scores[-1]["score"]


def add_score(name: str, score: int) -> None:
    """Add a score and keep only the best ones."""
    scores = load_scores()
    scores.append({"name": name.strip()[:10] or "PLAYER", "score": score})
    scores.sort(key=lambda item: item["score"], reverse=True)

    SCORES_FILE.parent.mkdir(parents=True, exist_ok=True)
    SCORES_FILE.write_text(
        json.dumps(scores[:MAX_SCORES], indent=2),
        encoding="utf-8",
    )