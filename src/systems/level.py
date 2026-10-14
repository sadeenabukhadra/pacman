"""Level system: maze from config.json + MazeAdapter (walls on cell edges)."""

import json
from collections import deque
from dataclasses import dataclass
from pathlib import Path

from src.maze.maze_adapter import MazeAdapter

CONFIG_PATH = Path("config.json")

# Wall bits of a generator cell (set bit = wall on that side)
BITS = {"up": 1, "right": 2, "down": 4, "left": 8}
OPPOSITE_DIR = {"up": "down", "down": "up", "left": "right", "right": "left"}
OFFSETS = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}
FULL = 15   # a fully closed cell = part of the "42" block


def load_config() -> dict:
    """Read config.json."""
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


@dataclass(frozen=True)
class LevelSettings:
    """Difficulty values of one level."""

    pacman_speed: float
    ghost_speed: float
    frightened_speed: float
    frightened_time: float


def settings_for_level(level: int) -> LevelSettings:
    """Return the difficulty of a level (it grows, then stays capped)."""
    step = min(level - 1, 10)
    return LevelSettings(
        pacman_speed=7.0 + 0.2 * step,
        ghost_speed=6.0 + 0.3 * step,
        frightened_speed=4.0,
        frightened_time=max(2.0, 8.0 - 0.6 * step),
    )


class Level:
    """Hold the maze state of the current level."""

    def __init__(self, number: int = 1) -> None:
        """Load the config and build the first maze."""
        self.config = load_config()
        cfg = self.config
        self.pellet_points = cfg.get("point_per_pacgum", 10)
        self.power_points = cfg.get(
            "point_per_super_pacgum",
            cfg.get("point_per_super_pacguem", 50),
        )
        self.ghost_points = cfg.get("point_per_ghost", 200)
        self.start_lives = cfg.get("lives", 3)

        self.tile = 8
        self.origin = (0, 0)
        self.number = number
        self._build()

    # -------------------------
    # Building
    # -------------------------

    def _build(self) -> None:
        """Generate the maze of the current level number."""
        sizes = self.config["level"]
        size = sizes[min(self.number - 1, len(sizes) - 1)]
        self.settings = settings_for_level(self.number)

        adapter = MazeAdapter(
            size["width"],
            size["height"],
            self.config["seed"] + self.number - 1,
        )
        self.cells = adapter.maze
        self.rows = len(self.cells)
        self.cols = len(self.cells[0])

        self.closed = {
            (x, y)
            for y in range(self.rows)
            for x in range(self.cols)
            if self.cells[y][x] == FULL
        }
        self.doors: set[tuple[int, int]] = set()

        left, top = 0, 0
        right, bottom = self.cols - 1, self.rows - 1
        self.pacman_start = (left, bottom)
        self.ghost_starts = {
            "red": (right, top),
            "pink": (left, top),
            "blue": (right, bottom),
            "yellow": (self.cols // 2, top),
        }
        self.house_center = (self.cols // 2, self.rows // 2)
        self.house_exit = self.house_center

        reachable = self._reachable(self.pacman_start)
        corners = {(left, top), (right, top), (left, bottom), (right, bottom)}
        self.power_pellets = (corners & reachable) - {self.pacman_start}
        self.pellets = reachable - self.power_pellets - {self.pacman_start}

    def _reachable(self, start: tuple[int, int]) -> set[tuple[int, int]]:
        """Return every cell Pac-Man can walk to."""
        seen = {start}
        queue = deque([start])
        while queue:
            col, row = queue.popleft()
            for target in self.neighbors(col, row).values():
                if target not in seen:
                    seen.add(target)
                    queue.append(target)
        return seen

    def reset(self) -> None:
        """Rebuild the same level (refill pellets)."""
        self._build()

    def next_level(self) -> None:
        """Move to the next level with a bigger maze."""
        self.number += 1
        self._build()

    # -------------------------
    # Queries
    # -------------------------

    @property
    def pellets_left(self) -> int:
        """Return how many pellets remain."""
        return len(self.pellets) + len(self.power_pellets)

    @property
    def is_cleared(self) -> bool:
        """Return True when every pellet is eaten."""
        return self.pellets_left == 0

    def wrap(self, col: int, row: int) -> tuple[int, int]:
        """Generated mazes have no side tunnels."""
        return col, row

    def is_wall(self, col: int, row: int, can_use_door: bool = False) -> bool:
        """Return True if a whole cell is not walkable."""
        if not (0 <= col < self.cols and 0 <= row < self.rows):
            return True
        return (col, row) in self.closed

    def can_pass(self, col: int, row: int, direction: str) -> bool:
        """Return True if there is no wall between a cell and its neighbor."""
        dx, dy = OFFSETS[direction]
        nx, ny = col + dx, row + dy
        if self.is_wall(col, row) or self.is_wall(nx, ny):
            return False
        if self.cells[row][col] & BITS[direction]:
            return False
        return not self.cells[ny][nx] & BITS[OPPOSITE_DIR[direction]]

    def neighbors(
        self,
        col: int,
        row: int,
        can_use_door: bool = False,
    ) -> dict[str, tuple[int, int]]:
        """Return the reachable neighbor cells by direction."""
        result = {}
        for direction, (dx, dy) in OFFSETS.items():
            if self.can_pass(col, row, direction):
                result[direction] = (col + dx, row + dy)
        return result

    def eat(self, col: int, row: int) -> tuple[int, bool]:
        """Eat what is on a cell; return (points, power_pellet_eaten)."""
        cell = (col, row)
        if cell in self.pellets:
            self.pellets.remove(cell)
            return self.pellet_points, False
        if cell in self.power_pellets:
            self.power_pellets.remove(cell)
            return self.power_points, True
        return 0, False

    # -------------------------
    # Geometry
    # -------------------------

    def fit_to(
        self,
        window_size: tuple[int, int],
        top_margin: int = 60,
        bottom_margin: int = 40,
    ) -> int:
        """Compute the tile size and origin so the maze fits the window."""
        width, height = window_size
        avail_h = height - top_margin - bottom_margin
        self.tile = max(6, min(width // self.cols, avail_h // self.rows))
        maze_w = self.cols * self.tile
        maze_h = self.rows * self.tile
        self.origin = (
            (width - maze_w) // 2,
            top_margin + (avail_h - maze_h) // 2,
        )
        return self.tile

    def cell_center(self, col: float, row: float) -> tuple[int, int]:
        """Return the pixel center of a (possibly fractional) cell."""
        return (
            round(self.origin[0] + (col + 0.5) * self.tile),
            round(self.origin[1] + (row + 0.5) * self.tile),
        )