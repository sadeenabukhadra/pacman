"""Maze collision helpers."""

from src.maze.maze import EAST, NORTH, SOUTH, WEST, Maze


class MazeCollision:
    """Handle collision checks between entities and the maze."""

    def __init__(
        self,
        maze: Maze,
        cell_size: int,
        offset_x: int = 0,
        offset_y: int = 0,
    ) -> None:
        """Initialize maze collision handling.

        Args:
            maze: Maze used by the current level.
            cell_size: Size of one maze cell in pixels.
            offset_x: Horizontal maze offset on the screen.
            offset_y: Vertical maze offset on the screen.
        """
        if cell_size <= 0:
            raise ValueError("cell_size must be greater than zero.")

        self.maze = maze
        self.cell_size = cell_size
        self.offset_x = offset_x
        self.offset_y = offset_y

    def pixel_to_cell(
        self,
        pixel_x: float,
        pixel_y: float,
    ) -> tuple[int, int]:
        """Convert pixel coordinates into maze cell coordinates.

        Args:
            pixel_x: Horizontal screen position.
            pixel_y: Vertical screen position.

        Returns:
            Maze cell coordinates as (x, y).
        """
        cell_x = int(
            (pixel_x - self.offset_x) // self.cell_size
        )
        cell_y = int(
            (pixel_y - self.offset_y) // self.cell_size
        )

        return cell_x, cell_y

    def cell_to_pixel(
        self,
        cell_x: int,
        cell_y: int,
    ) -> tuple[int, int]:
        """Convert maze cell coordinates to the top-left pixel position.

        Args:
            cell_x: Maze column.
            cell_y: Maze row.

        Returns:
            Top-left pixel coordinates of the cell.
        """
        pixel_x = self.offset_x + cell_x * self.cell_size
        pixel_y = self.offset_y + cell_y * self.cell_size

        return pixel_x, pixel_y

    def get_cell_center(
        self,
        cell_x: int,
        cell_y: int,
    ) -> tuple[int, int]:
        """Return the pixel center of a maze cell.

        Args:
            cell_x: Maze column.
            cell_y: Maze row.

        Returns:
            Pixel coordinates of the cell center.
        """
        pixel_x, pixel_y = self.cell_to_pixel(
            cell_x,
            cell_y,
        )

        center_x = pixel_x + self.cell_size // 2
        center_y = pixel_y + self.cell_size // 2

        return center_x, center_y

    def can_move(
        self,
        cell_x: int,
        cell_y: int,
        direction: int,
    ) -> bool:
        """Check whether movement is possible from a maze cell.

        Args:
            cell_x: Current maze column.
            cell_y: Current maze row.
            direction: NORTH, EAST, SOUTH, or WEST.

        Returns:
            True if movement is allowed, otherwise False.
        """
        if not self.maze.in_bounds(cell_x, cell_y):
            return False

        return self.maze.can_move(
            cell_x,
            cell_y,
            direction,
        )

    def can_move_from_pixel(
        self,
        pixel_x: float,
        pixel_y: float,
        direction: int,
    ) -> bool:
        """Check movement using an entity's pixel position.

        Args:
            pixel_x: Entity horizontal position.
            pixel_y: Entity vertical position.
            direction: NORTH, EAST, SOUTH, or WEST.

        Returns:
            True if movement is possible, otherwise False.
        """
        cell_x, cell_y = self.pixel_to_cell(
            pixel_x,
            pixel_y,
        )

        return self.can_move(
            cell_x,
            cell_y,
            direction,
        )

    def is_inside_maze(
        self,
        pixel_x: float,
        pixel_y: float,
    ) -> bool:
        """Check whether a pixel position belongs to the maze.

        Args:
            pixel_x: Horizontal screen position.
            pixel_y: Vertical screen position.

        Returns:
            True when the position is inside the maze.
        """
        cell_x, cell_y = self.pixel_to_cell(
            pixel_x,
            pixel_y,
        )

        return self.maze.in_bounds(cell_x, cell_y)

    @staticmethod
    def direction_from_delta(
        delta_x: int,
        delta_y: int,
    ) -> int | None:
        """Convert a movement delta into a maze direction.

        Args:
            delta_x: Horizontal movement direction.
            delta_y: Vertical movement direction.

        Returns:
            Maze direction or None for an invalid delta.
        """
        if delta_x == 0 and delta_y < 0:
            return NORTH

        if delta_x > 0 and delta_y == 0:
            return EAST

        if delta_x == 0 and delta_y > 0:
            return SOUTH

        if delta_x < 0 and delta_y == 0:
            return WEST

        return None