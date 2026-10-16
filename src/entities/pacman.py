"""Store Pac-Man state and move between open maze tiles."""

import math

import pygame

from src.maze.maze import Maze


DIRECTIONS: dict[str, tuple[int, int]] = {
    "up": (0, -1),
    "down": (0, 1),
    "left": (-1, 0),
    "right": (1, 0),
}
KEY_TO_DIRECTION: dict[int, str] = {
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
    """Move in tile coordinates while buffering the next requested turn.

    Integer coordinates refer to tile centers. Movement continues until
    a wall is reached; requested turns are applied at tile centers.
    """

    ANIMATION_INTERVAL = 0.12

    def __init__(self, maze: Maze, speed: float = 5.0) -> None:
        """Start on the open tile nearest the maze center.

        Args:
            maze: Expanded tile grid exposing in_bounds and is_wall.
            speed: Movement speed measured in tiles per second.

        Raises:
            ValueError: If speed is invalid or no open tile exists.
        """
        if not math.isfinite(speed) or speed <= 0:
            raise ValueError("Pac-Man speed must be positive and finite.")
        self.maze = maze
        self.speed = speed
        self.direction = "right"
        self.last_horizontal_direction = "right"
        self.requested_direction: str | None = None
        self.moving = False
        self.mouth_open = False
        self._animation_time = 0.0
        self._target: tuple[int, int] | None = None
        self._cell = self._find_spawn()
        self.x = float(self._cell[0])
        self.y = float(self._cell[1])

    def _find_spawn(self) -> tuple[int, int]:
        """Find a traversable tile as close as possible to the center."""
        center_x = (self.maze.width - 1) / 2
        center_y = (self.maze.height - 1) / 2
        candidates = (
            (x, y)
            for y in range(self.maze.height)
            for x in range(self.maze.width)
            if not self.maze.is_wall(x, y)
        )
        spawn = min(
            candidates,
            key=lambda p: (p[0] - center_x) ** 2
            + (p[1] - center_y) ** 2,
            default=None,
        )
        if spawn is None:
            raise ValueError("The maze has no open tile for Pac-Man.")
        return spawn

    def handle_event(self, event: pygame.event.Event) -> None:
        """Buffer arrow-key or WASD input until a turn is possible."""
        if event.type == pygame.KEYDOWN:
            direction = KEY_TO_DIRECTION.get(event.key)
            if direction is not None:
                self.request_direction(direction)

    def request_direction(self, direction: str) -> None:
        """Remember a valid direction for the next available tile center."""
        if direction not in DIRECTIONS:
            raise ValueError(f"Unknown Pac-Man direction: {direction}")
        self.requested_direction = direction

    def _next_tile(self, direction: str) -> tuple[int, int] | None:
        """Return an adjacent open tile, or None when blocked."""
        dx, dy = DIRECTIONS[direction]
        x, y = self._cell[0] + dx, self._cell[1] + dy
        if self.maze.in_bounds(x, y) and not self.maze.is_wall(x, y):
            return x, y
        return None

    def _choose_target(self) -> tuple[int, int] | None:
        """Apply a buffered turn if possible, otherwise keep moving."""
        if self.requested_direction is not None:
            target = self._next_tile(self.requested_direction)
            if target is not None:
                self.direction = self.requested_direction
                self.requested_direction = None
                return target
        return self._next_tile(self.direction)

    def update(self, dt: float) -> None:
        """Advance smoothly without crossing blocked tiles.

        Args:
            dt: Non-negative elapsed time in seconds.
        """
        if not math.isfinite(dt) or dt <= 0:
            return
        budget = self.speed * dt
        moved = 0.0
        while budget > 0:
            if self._target is None:
                self._target = self._choose_target()
            if self._target is None:
                break
            if self.direction in ("left", "right"):
                self.last_horizontal_direction = self.direction
            tx, ty = self._target
            distance = abs(tx - self.x) + abs(ty - self.y)
            step = min(budget, distance)
            dx, dy = DIRECTIONS[self.direction]
            self.x += dx * step
            self.y += dy * step
            budget -= step
            moved += step
            if distance <= step:
                self.x, self.y = float(tx), float(ty)
                self._cell = self._target
                self._target = None

        self.moving = (
            self._target is not None
            or self._next_tile(self.direction) is not None
        )
        if moved > 0 and self.moving:
            self._animation_time += moved / self.speed
            frame = int(self._animation_time / self.ANIMATION_INTERVAL)
            self.mouth_open = frame % 2 == 0
        else:
            self._animation_time = 0.0
            self.mouth_open = False