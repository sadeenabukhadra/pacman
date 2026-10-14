"""Maze model used by the game.

The maze generator returns a grid of *cells*, where every cell is a
bit mask of its walls (1 = north, 2 = east, 4 = south, 8 = west and
15 = a solid block, used for the "42").

The game works on a *tile* grid instead: every cell becomes a floor
tile, and every wall between two cells becomes one tile that is either
a wall or a floor. The tile grid is ``2 * size + 1`` tiles wide, so
walls have the same thickness as corridors, which is what the wall
sprites need.
"""

from collections.abc import Iterator

FLOOR = 0
WALL = 1

NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8

# dx, dy, wall bit
DIRECTIONS: tuple[tuple[int, int, int], ...] = (
    (0, -1, NORTH),
    (1, 0, EAST),
    (0, 1, SOUTH),
    (-1, 0, WEST),
)

SOLID_CELL = 15


class Maze:
    """Hold the tile grid of one level and answer questions about it."""

    def __init__(self, cells: list[list[int]]) -> None:
        """Build the tile grid from the generator cells.

        Args:
            cells: Grid of wall masks, indexed ``cells[y][x]``.

        Raises:
            ValueError: If the cells are empty or badly formed.
        """
        self._check_cells(cells)
        self.cells = cells
        self.cell_height = len(cells)
        self.cell_width = len(cells[0])
        self.width = self.cell_width * 2 + 1
        self.height = self.cell_height * 2 + 1
        self.tiles: list[list[int]] = self._build_tiles()
        self._remove_lonely_pillars()

    # -------------------------
    # Construction
    # -------------------------

    @staticmethod
    def _check_cells(cells: list[list[int]]) -> None:
        """Make sure the generator output can be used."""
        if not cells or not cells[0]:
            raise ValueError("maze is empty")

        width = len(cells[0])

        for row in cells:
            if len(row) != width:
                raise ValueError("maze rows have different lengths")
            for value in row:
                if type(value) is not int or not 0 <= value <= 15:
                    raise ValueError(f"invalid maze cell: {value!r}")

    def _build_tiles(self) -> list[list[int]]:
        """Expand the cells into a tile grid."""
        tiles = [[WALL] * self.width for _ in range(self.height)]

        for cy, row in enumerate(self.cells):
            for cx, value in enumerate(row):
                if value == SOLID_CELL:
                    continue

                tx = cx * 2 + 1
                ty = cy * 2 + 1
                tiles[ty][tx] = FLOOR

                for dx, dy, bit in DIRECTIONS:
                    if value & bit:
                        continue
                    nx = cx + dx
                    ny = cy + dy
                    if not self._cell_is_open(nx, ny):
                        continue
                    tiles[ty + dy][tx + dx] = FLOOR

        return tiles

    def _cell_is_open(self, cx: int, cy: int) -> bool:
        """Tell whether a cell exists and is not a solid block."""
        return (
            0 <= cx < self.cell_width
            and 0 <= cy < self.cell_height
            and self.cells[cy][cx] != SOLID_CELL
        )

    def _remove_lonely_pillars(self) -> None:
        """Turn wall corners that touch no other wall into floor.

        Once the maze is braided, some wall corners end up alone in the
        middle of a room. They look like stray dots, so they are removed.
        """
        for y in range(2, self.height - 1, 2):
            for x in range(2, self.width - 1, 2):
                if self.tiles[y][x] == WALL and self.wall_mask(x, y) == 0:
                    self.tiles[y][x] = FLOOR

    # -------------------------
    # Queries
    # -------------------------

    def in_bounds(self, x: int, y: int) -> bool:
        """Tell whether a tile position is inside the grid."""
        return 0 <= x < self.width and 0 <= y < self.height

    def is_wall(self, x: int, y: int) -> bool:
        """Tell whether a tile blocks movement (outside counts as wall)."""
        if not self.in_bounds(x, y):
            return True
        return self.tiles[y][x] == WALL

    def is_outer(self, x: int, y: int) -> bool:
        """Tell whether a tile is on the border of the maze."""
        return x in (0, self.width - 1) or y in (0, self.height - 1)

    def wall_mask(self, x: int, y: int) -> int:
        """Return which neighbours of a tile are walls.

        The result combines NORTH, EAST, SOUTH and WEST. Positions
        outside the grid do not count, so border walls only connect to
        their neighbours along the border.
        """
        mask = 0
        for dx, dy, bit in DIRECTIONS:
            nx = x + dx
            ny = y + dy
            if self.in_bounds(nx, ny) and self.tiles[ny][nx] == WALL:
                mask |= bit
        return mask

    def walls(self) -> Iterator[tuple[int, int]]:
        """Yield the position of every wall tile."""
        for y, row in enumerate(self.tiles):
            for x, value in enumerate(row):
                if value == WALL:
                    yield x, y

    def floors(self) -> Iterator[tuple[int, int]]:
        """Yield the position of every walkable tile."""
        for y, row in enumerate(self.tiles):
            for x, value in enumerate(row):
                if value == FLOOR:
                    yield x, y

    # -------------------------
    # Spawn points
    # -------------------------

    def nearest_floor(self, x: int, y: int) -> tuple[int, int]:
        """Return the walkable tile closest to a position."""
        return min(
            self.floors(),
            key=lambda pos: abs(pos[0] - x) + abs(pos[1] - y),
        )

    def corner_tiles(self) -> list[tuple[int, int]]:
        """Return the 4 corner tiles: top-left, top-right, bottom-left,
        bottom-right. Used for super-pacgums and ghost spawns."""
        last_x = self.width - 2
        last_y = self.height - 2
        return [(1, 1), (last_x, 1), (1, last_y), (last_x, last_y)]

    def player_spawn(self) -> tuple[int, int]:
        """Return the tile where the player starts (middle of the maze)."""
        return self.nearest_floor(self.width // 2, self.height // 2)