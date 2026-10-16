import pygame

from src.entities import Ghost, Pacman
from src.maze import Maze, MazeAdapter, MazeCollision
from src.core.input_handler import InputHandler


class Game:
    def __init__(
        self,
        width: int,
        height: int,
        seed: int,
        cell_size: int = 32,
    ) -> None:
        self.cell_size = cell_size

        adapter = MazeAdapter(
            width=width,
            height=height,
            seed=seed,
        )

        self.maze = Maze(adapter.maze)

        self.collision = MazeCollision(
            self.maze,
            self.cell_size,
        )

        self.input_handler = InputHandler()

        start_x = width // 2
        start_y = height // 2

        pacman_x, pacman_y = self.collision.get_cell_center(
            start_x,
            start_y,
        )

        self.pacman = Pacman(
            x=pacman_x,
            y=pacman_y,
            size=24,
            speed=4,
            collision=self.collision,
        )

        self.ghosts: list[Ghost] = []

        self.running = True

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.running = False
            return

        direction = self.input_handler.get_direction(event)

        if direction is not None:
            self.pacman.set_direction(direction)

    def update(self) -> None:
        self.pacman.update()

        for ghost in self.ghosts:
            ghost.update()

    def is_running(self) -> bool:
        return self.running