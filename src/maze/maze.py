from typing import Any

class Maze:
    def __init__(self,cells: list[list[int]]) -> None:
        self.cells = cells
        self.height = len(cells)
        self.width = len(cells)if cells else 0

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def has_wall(self, x: int, y: int, direction: dict[Any]) -> bool:
        ...

    def can_move(self, x: int, y: int, direction: dict[Any]) -> list:
        ...