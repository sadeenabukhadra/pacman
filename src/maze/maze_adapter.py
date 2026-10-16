from mazegenerator.mazegenerator import MazeGenerator


class MazeAdapter:
    def __init__(self, width: int, height: int, seed: int) -> None:
        self.width = width
        self.height = height
        self.seed = seed
        self.maze = self.maze_generator()

    def maze_generator(self) -> list[list[int]]:
        generator = MazeGenerator(
            size=(self.width, self.height),
            perfect=False,
            seed=self.seed,
        )
        return generator.maze
