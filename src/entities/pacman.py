import pygame

from src.maze import (
    MazeCollision,
    NORTH,
    EAST,
    SOUTH,
    WEST,
)


class Pacman:
    def __init__(
        self,
        x: int,
        y: int,
        size: int,
        speed: int,
        collision: MazeCollision,
    ) -> None:
        self.rect = pygame.Rect(x, y, size, size)
        self.speed = speed
        self.collision = collision

        self.direction = EAST
        self.next_direction = EAST

    def set_direction(self, direction: int) -> None:
        self.next_direction = direction

    def update(self) -> None:
        if self.collision.can_move(
            self.rect,
            self.next_direction,
        ):
            self.direction = self.next_direction

        self.rect = self.collision.resolve_movement(
            self.rect,
            self.direction,
            self.speed,
        )

    def get_position(self) -> tuple[int, int]:
        return self.rect.x, self.rect.y