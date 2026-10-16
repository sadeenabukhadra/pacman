"""Represent a super-pacgum that temporarily makes ghosts edible."""

import math
from dataclasses import dataclass

from src.entities.pellet import Pellet


@dataclass
class PowerCrystal(Pellet):
    """Store a power pellet's position, score and effect duration.

    Gameplay applies the effect to ghosts after consume() succeeds.
    Rendering selects the ice or cosmic sprite from the current theme.
    """

    points: int = 50
    duration: float = 7.0

    def __post_init__(self) -> None:
        """Validate inherited fields and the positive effect duration.

        Raises:
            ValueError: If position, score or duration is invalid.
        """
        super().__post_init__()
        if (
            isinstance(self.duration, bool)
            or not isinstance(self.duration, (int, float))
            or not math.isfinite(self.duration)
            or self.duration <= 0
        ):
            raise ValueError("Power duration must be positive and finite.")

    @property
    def is_super(self) -> bool:
        """Return True to distinguish this collectible from normal pellets."""
        return True