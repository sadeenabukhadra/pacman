from typing import Final

NORTH: Final = 1
EAST: Final = 2
SOUTH: Final = 4
WEST: Final = 8

class Maze:
    def __init__(self,cells: list[list[int]]) -> None:
        self.cells = cells
        self.height = len(cells)
        self.width = len(cells)if cells else 0


    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def has_wall(self, x: int, y: int, direction: dict[int]) -> bool:
        cell = self.cells[x][y]
        return bool(cell & direction)

    def can_moves(self, x: int, y: int, direction: dict[int]) -> bool:
        if not self.in_bounds(x, y):
            return False

        if self.has_wall(x, y, direction):
            return False

        if direction == NORTH:
            new_x = x
            new_y = y + 1

        elif direction == EAST:
            new_x = x + 1
            new_y = y

        elif direction == SOUTH:
            new_x = x
            new_y = y - 1

        elif direction == WEST:
            new_x = x - 1
            new_y = y

        else:
            return False

        return self.in_bounds(new_x, new_y)