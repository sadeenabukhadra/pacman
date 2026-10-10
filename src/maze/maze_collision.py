import pygame

from src.maze.maze import Maze, NORTH, EAST, SOUTH, WEST


class MazeCollision:
    def __init__(self, maze: Maze, cell_size: int) -> None:
        self.maze = maze
        self.cell_size = cell_size

    def pixel_to_cell(self, x: int, y: int) -> tuple[int, int]:
        """Convert pixel position to maze cell coordinates."""
        cell_x = x // self.cell_size
        cell_y = y // self.cell_size

        return cell_x, cell_y

    def get_cell_center(self, cell_x: int, cell_y: int) -> tuple[int, int]:
        """Return the pixel center of a maze cell."""
        center_x = cell_x * self.cell_size + self.cell_size // 2
        center_y = cell_y * self.cell_size + self.cell_size // 2

        return center_x, center_y

    def is_centered_in_cell(
        self,
        rect: pygame.Rect,
        tolerance: int = 2,
    ) -> bool:
        """Check whether an entity is near the center of its cell."""
        cell_x, cell_y = self.pixel_to_cell(
            rect.centerx,
            rect.centery,
        )

        center_x, center_y = self.get_cell_center(
            cell_x,
            cell_y,
        )

        return (
            abs(rect.centerx - center_x) <= tolerance
            and abs(rect.centery - center_y) <= tolerance
        )

    def can_move(
        self,
        rect: pygame.Rect,
        direction: int,
    ) -> bool:
        """Check whether movement is allowed in a direction."""
        cell_x, cell_y = self.pixel_to_cell(
            rect.centerx,
            rect.centery,
        )

        if not self.maze.in_bounds(cell_x, cell_y):
            return False

        return self.maze.can_move(
            cell_x,
            cell_y,
            direction,
        )

    def will_hit_wall(
        self,
        rect: pygame.Rect,
        direction: int,
        speed: int,
    ) -> bool:
        """Check whether the next movement will cross a wall."""
        new_rect = rect.copy()

        if direction == NORTH:
            new_rect.y -= speed

        elif direction == EAST:
            new_rect.x += speed

        elif direction == SOUTH:
            new_rect.y += speed

        elif direction == WEST:
            new_rect.x -= speed

        else:
            return True

        current_cell = self.pixel_to_cell(
            rect.centerx,
            rect.centery,
        )

        next_cell = self.pixel_to_cell(
            new_rect.centerx,
            new_rect.centery,
        )

        if current_cell == next_cell:
            return False

        cell_x, cell_y = current_cell

        return not self.maze.can_move(
            cell_x,
            cell_y,
            direction,
        )

    def resolve_movement(
        self,
        rect: pygame.Rect,
        direction: int,
        speed: int,
    ) -> pygame.Rect:
        """Return the entity position after applying valid movement."""
        if self.will_hit_wall(rect, direction, speed):
            return rect.copy()

        new_rect = rect.copy()

        if direction == NORTH:
            new_rect.y -= speed

        elif direction == EAST:
            new_rect.x += speed

        elif direction == SOUTH:
            new_rect.y += speed

        elif direction == WEST:
            new_rect.x -= speed

        return new_rect