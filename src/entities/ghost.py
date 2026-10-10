import random
import pygame

from src.maze import (
    MazeCollision,
    NORTH,
    EAST,
    SOUTH,
    WEST,
)


class Ghost:
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

    def choose_direction(self) -> None:
        directions = [
            NORTH,
            EAST,
            SOUTH,
            WEST,
        ]

        valid_directions = []

        for direction in directions:
            if self.collision.can_move(
                self.rect,
                direction,
            ):
                valid_directions.append(direction)

        if valid_directions:
            self.direction = random.choice(valid_directions)

    def update(self) -> None:
        if not self.collision.can_move(
            self.rect,
            self.direction,
        ):
            self.choose_direction()

        self.rect = self.collision.resolve_movement(
            self.rect,
            self.direction,
            self.speed,
        )

    def get_position(self) -> tuple[int, int]:
        return self.rect.x, self.rect.y