"""Place and collect normal pellets and corner power pellets."""

import math
from collections import deque
from collections.abc import Iterator
from random import Random

from src.entities.pellet import Pellet
from src.entities.power_crystal import PowerCrystal
from src.maze.maze import Maze


Cell = tuple[int, int]


class Collectibles:
    """Manage collectibles on reachable floor tiles of one maze.

    By default every reachable floor tile receives a pellet, except
    the player's start and the four tiles reserved for power pellets.
    An explicit pacgum_count instead selects that many normal pellets,
    clamped to the number of available tiles.
    """

    def __init__(
        self,
        maze: Maze,
        player_spawn: Cell,
        pacgum_count: int | None = None,
        points_per_pacgum: int = 10,
        points_per_super_pacgum: int = 50,
        power_duration: float = 7.0,
        seed: int = 42,
    ) -> None:
        """Place pellets without changing walls or generator output.

        Args:
            maze: Expanded maze used by player movement.
            player_spawn: Open tile to keep free of collectibles.
            pacgum_count: Normal pellet limit, or None to fill corridors.
            points_per_pacgum: Score awarded for an ordinary pellet.
            points_per_super_pacgum: Score awarded for a power pellet.
            power_duration: Ghost fright duration in seconds.
            seed: Independent random seed for limited pellet placement.

        Raises:
            ValueError: If settings are invalid or fewer than four
                reachable floor tiles besides the player start exist.
        """
        if not maze.in_bounds(*player_spawn) or maze.is_wall(*player_spawn):
            raise ValueError("Player spawn must be an open maze tile.")
        if pacgum_count is not None:
            if type(pacgum_count) is not int or pacgum_count < 0:
                raise ValueError("Pacgum count must be a non-negative int.")
        # Validate settings even if there will be no ordinary pellets.
        Pellet(0, 0, points=points_per_pacgum)
        PowerCrystal(
            0, 0, points=points_per_super_pacgum, duration=power_duration,
        )
        self.maze = maze
        self._items: dict[Cell, Pellet] = {}
        available = self._reachable(player_spawn)
        available.remove(player_spawn)
        if len(available) < 4:
            raise ValueError("Four reachable tiles are needed for power pellets.")
        corners = (
            (1, 1), (maze.width - 2, 1),
            (1, maze.height - 2), (maze.width - 2, maze.height - 2),
        )
        for cx, cy in corners:
            position = min(
                available,
                key=lambda tile: (
                    abs(tile[0] - cx) + abs(tile[1] - cy),
                    tile[1], tile[0],
                ),
            )
            available.remove(position)
            self._items[position] = PowerCrystal(
                *position,
                points=points_per_super_pacgum,
                duration=power_duration,
            )
        positions = sorted(available)
        if pacgum_count is not None:
            positions = Random(seed).sample(
                positions, min(pacgum_count, len(positions)),
            )
        for position in positions:
            self._items[position] = Pellet(
                *position, points=points_per_pacgum,
            )

    def _reachable(self, start: Cell) -> set[Cell]:
        """Find only floor tiles reachable from the player's start."""
        reached = {start}
        queue: deque[Cell] = deque([start])
        while queue:
            x, y = queue.popleft()
            for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
                tile = (x + dx, y + dy)
                if (
                    tile not in reached
                    and self.maze.in_bounds(*tile)
                    and not self.maze.is_wall(*tile)
                ):
                    reached.add(tile)
                    queue.append(tile)
        return reached

    @property
    def remaining(self) -> int:
        """Return the number of uneaten normal and power pellets."""
        return len(self._items)

    @property
    def remaining_regular(self) -> int:
        """Return the number of ordinary pellets still present."""
        return sum(not item.is_super for item in self._items.values())

    @property
    def remaining_super(self) -> int:
        """Return the number of power pellets still present."""
        return sum(item.is_super for item in self._items.values())

    def active_pellets(self) -> Iterator[Pellet]:
        """Yield remaining pellets for drawing; do not mutate while iterating."""
        yield from self._items.values()

    def collect_at(
        self, x: float, y: float, radius: float = 0.45,
    ) -> list[Pellet]:
        """Remove nearby pellets and return them for score/effect handling.

        Coordinates and radius use tile units. Call during small movement
        steps so fast movement cannot skip a pellet. Radius must stay
        below half a tile to avoid collecting through adjacent walls.

        Raises:
            ValueError: If coordinates or radius are invalid.
        """
        if not all(math.isfinite(value) for value in (x, y, radius)):
            raise ValueError("Collection coordinates must be finite.")
        if not 0 < radius < 0.5:
            raise ValueError("Collection radius must be between 0 and 0.5.")
        collected: list[Pellet] = []
        for ty in range(math.ceil(y - radius), math.floor(y + radius) + 1):
            for tx in range(math.ceil(x - radius), math.floor(x + radius) + 1):
                if (tx - x) ** 2 + (ty - y) ** 2 > radius ** 2:
                    continue
                item = self._items.pop((tx, ty), None)
                if item is not None and item.consume():
                    collected.append(item)
        return collected
