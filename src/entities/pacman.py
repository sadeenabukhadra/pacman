"""Pac-Man entity: grid movement, input and eating."""

import pygame

from src.systems.level import Level
from src.systems.movement import (
    DIRS,
    OPPOSITE,
    advance,
    can_move,
    reverse,
)


KEY_TO_DIRECTION = {
    pygame.K_UP: "up",
    pygame.K_w: "up",
    pygame.K_DOWN: "down",
    pygame.K_s: "down",
    pygame.K_LEFT: "left",
    pygame.K_a: "left",
    pygame.K_RIGHT: "right",
    pygame.K_d: "right",
}


class Pacman:
    """Move on the maze grid and eat pellets."""

    def __init__(self, level: Level) -> None:
        """Place Pac-Man on the level start cell."""
        self.level = level
        self.reset()

    def reset(self) -> None:
        """Return to the start cell."""
        self.col, self.row = self.level.pacman_start

        self.x = float(self.col)
        self.y = float(self.row)

        self.direction: str = "right"
        self.desired: str | None = None
        self.facing: str = "right"

        self.target: tuple[int, int] | None = None
        self.moving = False

        self._points = 0
        self._power = False

    def handle_event(
        self,
        event: pygame.event.Event,
    ) -> None:
        """Read a direction key."""
        if event.type != pygame.KEYDOWN:
            return

        direction = KEY_TO_DIRECTION.get(
            event.key
        )

        if direction is None:
            return

        self.desired = direction

        if (
            self.target is not None
            and direction == OPPOSITE[self.direction]
        ):
            reverse(self)
            self.facing = self.direction

    def _choose_direction(self) -> None:
        """Choose movement direction at a cell center."""
        if (
            self.desired is not None
            and can_move(
                self.level,
                self.col,
                self.row,
                self.desired,
            )
        ):
            self.direction = self.desired

        elif not can_move(
            self.level,
            self.col,
            self.row,
            self.direction,
        ):
            self.target = None
            self.moving = False
            return

        self.moving = True
        self.facing = self.direction

        dx, dy = DIRS[
            self.direction
        ]

        self.target = (
            self.col + dx,
            self.row + dy,
        )

    def _on_arrive(
        self,
        _entity,
    ) -> None:
        """Eat what is on the reached cell."""
        earned, is_power = self.level.eat(
            self.col,
            self.row,
        )

        self._points += earned

        self._power = (
            self._power
            or is_power
        )

    def update(
        self,
        dt: float,
    ) -> tuple[int, bool]:
        """Move and return earned points."""
        self._points = 0
        self._power = False

        advance(
            self,
            self.level.settings.pacman_speed * dt,
            self._choose_direction,
            self._on_arrive,
        )

        return (
            self._points,
            self._power,
        )

    def draw(
        self,
        surface: pygame.Surface,
        graphics,
    ) -> None:
        """Draw Pac-Man."""
        graphics.blit_center(
            surface,
            graphics.get_pacman(
                self.facing
            ),
            self.level.cell_center(
                self.x,
                self.y,
            ),
        )