"""Move ghosts through maze tiles and manage their gameplay states."""

import math
from typing import Protocol, cast

from src.maze.maze import Maze
from src.systems.ghost_ai import (
    STEPS, Cell, Direction, GhostAI, GhostColor, GhostMode,
)


class PlayerPosition(Protocol):
    """Player attributes required by ghost movement and targeting."""

    x: float
    y: float
    direction: str


class Ghost:
    """Store one ghost's position, personality, home and state timers.

    Positions use the same tile-center coordinates as Pac-Man. Each
    movement decision is made at a tile center by GhostAI.
    """

    RESPAWN_DELAY = 5.0
    FLASH_DURATION = 2.0
    FLASH_INTERVAL = 0.15

    def __init__(
        self,
        maze: Maze,
        color: GhostColor,
        spawn: Cell,
        speed: float = 4.0,
        ai: GhostAI | None = None,
    ) -> None:
        """Create a ghost on an open corner tile.

        Args:
            maze: Maze used for movement and pathfinding.
            color: Red, pink, blue or yellow personality.
            spawn: Open tile assigned as this ghost's home corner.
            speed: Normal speed in tiles per second.
            ai: Optional strategy selector using the same maze.

        Raises:
            ValueError: If color, spawn, speed or AI maze is invalid.
        """
        if color not in ("red", "pink", "blue", "yellow"):
            raise ValueError(f"Unknown ghost color: {color}")
        if not math.isfinite(speed) or speed <= 0:
            raise ValueError("Ghost speed must be positive and finite.")
        if not maze.in_bounds(*spawn) or maze.is_wall(*spawn):
            raise ValueError(f"Ghost spawn must be an open tile: {spawn}")
        if ai is not None and ai.maze is not maze:
            raise ValueError("Ghost and AI must use the same maze.")
        self.maze = maze
        self.color: GhostColor = color
        self.home = spawn
        self.speed = speed
        self.ai = ai if ai is not None else GhostAI(maze)
        self.direction: Direction = "right"
        self.last_horizontal_direction: Direction = "right"
        self.mode: GhostMode = "normal"
        self.x = float(spawn[0])
        self.y = float(spawn[1])
        self._cell = spawn
        self._target: Cell | None = None
        self._frightened_remaining = 0.0
        self._respawn_remaining = 0.0

    @property
    def frightened_remaining(self) -> float:
        """Return remaining power-pellet effect time in seconds."""
        return self._frightened_remaining

    @property
    def edible(self) -> bool:
        """Return whether Pac-Man can currently eat this ghost."""
        return self.mode == "frightened"

    @property
    def dangerous(self) -> bool:
        """Return whether touching this ghost should cost a player life."""
        return self.mode == "normal"

    @property
    def flashing(self) -> bool:
        """Select alternating flash frames near the end of fright."""
        return (
            self.edible
            and self._frightened_remaining <= self.FLASH_DURATION
            and int(self._frightened_remaining / self.FLASH_INTERVAL) % 2 == 0
        )

    @property
    def waiting_at_home(self) -> bool:
        """Return whether an eaten ghost is waiting before revival."""
        return self._respawn_remaining > 0

    def reset(self) -> None:
        """Restore the normal state and place the ghost at its home."""
        self.x, self.y = float(self.home[0]), float(self.home[1])
        self._cell = self.home
        self._target = None
        self.direction = "right"
        self.last_horizontal_direction = "right"
        self.mode = "normal"
        self._frightened_remaining = 0.0
        self._respawn_remaining = 0.0

    def frighten(self, seconds: float = 7.0) -> None:
        """Start or refresh fright; returning eyes ignore power pellets.

        Raises:
            ValueError: If duration is negative or non-finite.
        """
        if not math.isfinite(seconds) or seconds < 0:
            raise ValueError(
                "Fright duration must be finite and non-negative.")
        if self.mode == "eaten" or seconds == 0:
            return
        self.mode = "frightened"
        self._frightened_remaining = seconds

    def eat(self) -> bool:
        """Become returning eyes if edible; report whether eating succeeded."""
        if not self.edible:
            return False
        self.mode = "eaten"
        self._frightened_remaining = 0.0
        return True

    def _choose_target(self, player: PlayerPosition) -> None:
        """Choose a legal next tile using the current state and personality."""
        if player.direction not in STEPS:
            raise ValueError("Player direction is invalid.")
        direction = self.ai.choose_direction(
            color=self.color,
            cell=self._cell,
            current_direction=self.direction,
            player_cell=(round(player.x), round(player.y)),
            player_direction=cast(Direction, player.direction),
            mode=self.mode,
            home=self.home,
        )
        if direction is None:
            return
        dx, dy = STEPS[direction]
        target = (self._cell[0] + dx, self._cell[1] + dy)
        if self.maze.in_bounds(*target) and not self.maze.is_wall(*target):
            self.direction = direction
            self._target = target
            if direction in ("left", "right"):
                self.last_horizontal_direction = direction

    def _move(self, seconds: float, player: PlayerPosition) -> float:
        """Move for a time slice; stop the slice early on returning home."""
        factor = 1.75 if self.mode == "eaten" else 1.0
        if self.mode == "frightened":
            factor = 0.70
        speed = self.speed * factor
        budget = speed * seconds
        travelled = 0.0
        while budget > 0:
            if self.mode == "eaten" and self._target is None:
                if self._cell == self.home:
                    self._respawn_remaining = self.RESPAWN_DELAY
                    return travelled / speed
            if self._target is None:
                self._choose_target(player)
            if self._target is None:
                return seconds
            tx, ty = self._target
            distance = abs(tx - self.x) + abs(ty - self.y)
            step = min(budget, distance)
            dx, dy = STEPS[self.direction]
            self.x += dx * step
            self.y += dy * step
            budget -= step
            travelled += step
            if step >= distance:
                self.x, self.y = float(tx), float(ty)
                self._cell = self._target
                self._target = None
        return seconds

    def update(self, dt: float, player: PlayerPosition) -> None:
        """Advance movement, fright expiry and home revival timers.

        Args:
            dt: Elapsed frame time in seconds.
            player: Current Pac-Man position and direction.
        """
        if not math.isfinite(dt) or dt <= 0:
            return
        remaining = dt
        while remaining > 0:
            if self._respawn_remaining > 0:
                used = min(remaining, self._respawn_remaining)
                self._respawn_remaining -= used
                remaining -= used
                if self._respawn_remaining == 0:
                    self.mode = "normal"
                continue
            interval = remaining
            if self.mode == "frightened":
                interval = min(interval, self._frightened_remaining)
            used = self._move(interval, player)
            remaining -= used
            if self.mode == "frightened":
                self._frightened_remaining = max(
                    0.0, self._frightened_remaining - used,
                )
                if self._frightened_remaining == 0:
                    self.mode = "normal"
