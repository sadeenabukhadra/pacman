"""Generate subsequent configured levels through the assigned package."""

from random import SystemRandom

from mazegenerator.mazegenerator import MazeGenerator

from src.config.config_validater import GameConfig
from src.maze.maze import Maze


class LevelProgression:
    """Track configured levels without resetting a run's score or lives."""

    def __init__(self, config: GameConfig) -> None:
        """Keep an independent copy of dimensions and the first level seed."""
        self.dimensions = tuple(
            (level["width"], level["height"]) for level in config["level"]
        )
        if not self.dimensions:
            raise ValueError("At least one level is required.")
        self.index = 0
        self.seed = config["seed"]
        self._random = SystemRandom()

    @property
    def is_last(self) -> bool:
        """Report whether completing this level should win the run."""
        return self.index + 1 >= len(self.dimensions)

    def prepare_next(self) -> tuple[Maze, int]:
        """Build a random next maze without advancing on generator failure."""
        if self.is_last:
            raise ValueError("There is no level after the final level.")
        seed = self._random.randrange(1, 2**31)
        if seed == self.seed:
            seed = seed % (2**31 - 1) + 1
        try:
            generator = MazeGenerator(
                size=self.dimensions[self.index + 1],
                perfect=False,
                seed=seed,
            )
            maze = Maze(generator.maze)
        except Exception as error:
            raise RuntimeError(
                "The next maze could not be generated.",
            ) from error
        return maze, seed

    def commit_next(self, seed: int) -> None:
        """Advance only after the next level's actors and drawing are ready."""
        if self.is_last:
            raise ValueError("Cannot advance past the final level.")
        self.index += 1
        self.seed = seed
