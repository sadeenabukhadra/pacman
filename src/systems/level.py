from typing import Any
from src.maze.maze import Maze
from src.maze import MazeAdapter


class LevelManager:
    def __init__(self, config: dict[str, Any]) -> None:
        self.levels = config["level"]
        self.seed = config["seed"]
        self.current_index = 0
        self.maze: list[list[int]] = []

    def start_level(self) -> None:
        level_settings = self.levels[self.current_index]

        level_seed = self.seed if self.current_index == 0 else 0

        adapter = MazeAdapter(
            width=level_settings["width"],
            height=level_settings["height"],
            seed=level_seed,
        )
        self.maze = Maze(adapter.maze)

    def next_level(self) -> bool:
        if self.current_index + 1 >= len(self.levels):
            return False

        self.current_index += 1
        self.start_level()
        return True
