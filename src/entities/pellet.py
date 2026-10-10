import pygame


class Pellet:
    def __init__(
        self,
        x: int,
        y: int,
        radius: int,
        points: int,
        is_super: bool = False,
    ) -> None:
        self.x = x
        self.y = y
        self.radius = radius
        self.points = points
        self.is_super = is_super
        self.eaten = False

    def get_position(self) -> tuple[int, int]:
        return self.x, self.y

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(
            self.x - self.radius,
            self.y - self.radius,
            self.radius * 2,
            self.radius * 2,
        )

    def eat(self) -> int:
        self.eaten = True
        return self.points

    def is_eaten(self) -> bool:
        return self.eaten