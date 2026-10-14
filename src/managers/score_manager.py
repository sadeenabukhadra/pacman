"""Manage loading, checking and saving high scores."""

import json
from pathlib import Path


SCORE_FILE = Path("high_scor.json")
MAX_SCORES = 10


def load_scores() -> list[dict[str, int | str]]:
    """Load high scores from the score file."""
    if not SCORE_FILE.exists():
        return []

    try:
        data = json.loads(
            SCORE_FILE.read_text(
                encoding="utf-8",
            )
        )
    except (
        json.JSONDecodeError,
        OSError,
    ):
        return []

    if not isinstance(
        data,
        list,
    ):
        return []

    scores: list[
        dict[str, int | str]
    ] = []

    for item in data:
        if not isinstance(
            item,
            dict,
        ):
            continue

        name = item.get(
            "name"
        )

        score = item.get(
            "score"
        )

        if not isinstance(
            name,
            str,
        ):
            continue

        if not isinstance(
            score,
            int,
        ):
            continue

        scores.append(
            {
                "name": name,
                "score": score,
            }
        )

    scores.sort(
        key=lambda item: int(
            item["score"]
        ),
        reverse=True,
    )

    return scores[
        :MAX_SCORES
    ]


def save_scores(
    scores: list[dict[str, int | str]],
) -> None:
    """Save high scores to the score file."""
    SCORE_FILE.write_text(
        json.dumps(
            scores,
            indent=4,
        ),
        encoding="utf-8",
    )


def is_high_score(
    score: int,
) -> bool:
    """Return True if the score belongs in the high-score table."""
    scores = load_scores()

    if len(scores) < MAX_SCORES:
        return True

    lowest_score = int(
        scores[-1]["score"]
    )

    return score > lowest_score


def add_score(
    name: str,
    score: int,
) -> None:
    """Add a score and keep only the best scores."""
    scores = load_scores()

    scores.append(
        {
            "name": name,
            "score": score,
        }
    )

    scores.sort(
        key=lambda item: int(
            item["score"]
        ),
        reverse=True,
    )

    scores = scores[
        :MAX_SCORES
    ]

    save_scores(
        scores
    )