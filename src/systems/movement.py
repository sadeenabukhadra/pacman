import pygame

from src.maze import NORTH, EAST, SOUTH, WEST
from src.maze import MazeCollision


class MovementSystem:
    def __init__(self, collision: MazeCollision) -> None:
        self.collision = collision

    def move(
        self,
        rect: pygame.Rect,
        direction: int,
        speed: int,
    ) -> pygame.Rect:
        return self.collision.resolve_movement(
            rect,
            direction,
            speed,
        )

    def can_move(
        self,
        rect: pygame.Rect,
        direction: int,
    ) -> bool:
        return self.collision.can_move(
            rect,
            direction,
        )

    def get_direction_vector(
        self,
        direction: int,
    ) -> tuple[int, int]:
        if direction == NORTH:
            return 0, -1

        if direction == EAST:
            return 1, 0

        if direction == SOUTH:
            return 0, 1

        if direction == WEST:
            return -1, 0

        return 0, 0