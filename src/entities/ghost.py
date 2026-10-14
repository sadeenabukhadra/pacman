"""Ghost entity: grid movement with normal, frightened and eaten modes."""

import random

import pygame

from src.systems.level import Level
from src.systems.movement import (
    DIRS,
    OPPOSITE,
    advance,
    cell_distance_sq,
    manhattan,
    reverse,
)


RELEASE_TIMES = {
    "red": 0.0,
    "pink": 2.0,
    "blue": 4.0,
    "yellow": 6.0,
}


class Ghost:
    """A ghost that moves cell to cell."""

    def __init__(
        self,
        level: Level,
        color: str,
    ) -> None:
        """Create a ghost at its start position."""
        self.level = level
        self.color = color
        self._pacman = None

        self.reset()

    def reset(self) -> None:
        """Return ghost to its start position."""
        self.home = self.level.ghost_starts[
            self.color
        ]

        self.col, self.row = self.home

        self.x = float(self.col)
        self.y = float(self.row)

        self.direction = "left"

        self.target: tuple[int, int] | None = None

        self.mode = "normal"

        self.frightened_left = 0.0

        self.release_timer = RELEASE_TIMES[
            self.color
        ]

    # ==========================================================
    # State
    # ==========================================================

    def frighten(
        self,
        seconds: float,
    ) -> None:
        """Make the ghost frightened."""
        if self.mode == "eaten":
            return

        self.mode = "frightened"
        self.frightened_left = seconds

        reverse(self)

    def eat(self) -> None:
        """Change ghost to eaten mode."""
        self.mode = "eaten"

        self.target = None

    @property
    def is_flashing(self) -> bool:
        """Return True during frightened flashing period."""
        return (
            self.mode == "frightened"
            and self.frightened_left < 2.0
            and int(
                self.frightened_left * 5
            ) % 2 == 0
        )

    # ==========================================================
    # Target
    # ==========================================================

    def _goal(
        self,
        pacman,
    ) -> tuple[int, int]:
        """Return the target cell for this ghost."""

        if self.mode == "eaten":
            return self.home

        # Red follows Pac-Man directly
        if self.color == "red":
            return (
                pacman.col,
                pacman.row,
            )

        dx, dy = DIRS[
            pacman.facing
        ]

        # Pink aims ahead of Pac-Man
        if self.color == "pink":
            return (
                pacman.col + 4 * dx,
                pacman.row + 4 * dy,
            )

        # Blue uses another target around Pac-Man
        if self.color == "blue":
            return (
                pacman.col - 2 * dx,
                pacman.row - 2 * dy,
            )

        # Yellow follows from far away
        distance = manhattan(
            (
                self.col,
                self.row,
            ),
            (
                pacman.col,
                pacman.row,
            ),
        )

        if distance > 8:
            return (
                pacman.col,
                pacman.row,
            )

        return (
            1,
            self.level.rows - 2,
        )

    # ==========================================================
    # Movement
    # ==========================================================

    def _choose_direction(self) -> None:
        """Choose the next direction."""

        options = self.level.neighbors(
            self.col,
            self.row,
        )

        if not options:
            self.target = None
            return

        back = OPPOSITE[
            self.direction
        ]

        choices = {
            direction: cell
            for direction, cell in options.items()
            if direction != back
        }

        if not choices:
            choices = options

        # -------------------------
        # Frightened movement
        # -------------------------

        if self.mode == "frightened":
            self.direction = random.choice(
                list(
                    choices.keys()
                )
            )

        # -------------------------
        # Normal / eaten movement
        # -------------------------

        else:
            goal = self._goal(
                self._pacman
            )

            self.direction = min(
                choices,
                key=lambda direction: cell_distance_sq(
                    choices[direction],
                    goal,
                ),
            )

        # Important:
        # target must be assigned in every mode.
        self.target = choices[
            self.direction
        ]

    def _on_arrive(
        self,
        _entity,
    ) -> None:
        """Handle arriving at a cell."""

        if (
            self.mode == "eaten"
            and (
                self.col,
                self.row,
            ) == self.home
        ):
            self.mode = "normal"

            self.release_timer = 1.5

    def _speed(self) -> float:
        """Return ghost speed."""

        settings = self.level.settings

        if self.mode == "eaten":
            return (
                settings.ghost_speed
                * 2.0
            )

        if self.mode == "frightened":
            return settings.frightened_speed

        return settings.ghost_speed

    def update(
        self,
        dt: float,
        pacman,
    ) -> None:
        """Update ghost movement."""

        # Wait before release
        if self.release_timer > 0:
            self.release_timer -= dt
            return

        # Frightened timer
        if self.mode == "frightened":
            self.frightened_left -= dt

            if self.frightened_left <= 0:
                self.frightened_left = 0.0
                self.mode = "normal"

        self._pacman = pacman

        advance(
            self,
            self._speed() * dt,
            self._choose_direction,
            self._on_arrive,
        )

    # ==========================================================
    # Collision
    # ==========================================================

    def touches(
        self,
        pacman,
    ) -> bool:
        """Return True if Pac-Man touches the ghost."""

        distance = (
            abs(
                self.x - pacman.x
            )
            + abs(
                self.y - pacman.y
            )
        )

        return distance < 0.6

    # ==========================================================
    # Drawing
    # ==========================================================

    def draw(
        self,
        surface: pygame.Surface,
        graphics,
    ) -> None:
        """Draw ghost depending on its state."""

        if self.mode == "eaten":
            image = graphics.get_eyes(
                self.direction
            )

        elif self.mode == "frightened":
            image = graphics.get_frightened(
                self.direction,
                self.is_flashing,
            )

        else:
            image = graphics.get_ghost(
                self.color,
                self.direction,
            )

        graphics.blit_center(
            surface,
            image,
            self.level.cell_center(
                self.x,
                self.y,
            ),
        )