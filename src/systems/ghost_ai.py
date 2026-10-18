"""Choose legal ghost directions using distinct pursuit strategies."""

from collections import deque
from random import Random
from typing import Literal

from src.maze.maze import Maze


Direction = Literal["up", "down", "left", "right"]
GhostColor = Literal["red", "pink", "blue", "yellow"]
GhostMode = Literal["normal", "frightened", "eaten"]
Cell = tuple[int, int]

STEPS: dict[Direction, Cell] = {
    "up": (0, -1),
    "down": (0, 1),
    "left": (-1, 0),
    "right": (1, 0),
}
OPPOSITE: dict[Direction, Direction] = {
    "up": "down",
    "down": "up",
    "left": "right",
    "right": "left",
}


class GhostAI:
    """Select a direction at tile centers without changing entity state.

    Red follows shortest paths. Pink greedily aims ahead of the player.
    Blue mixes greedy pursuit with exploration. Yellow mostly explores.
    Frightened ghosts maximize maze distance from the player; eaten
    ghosts follow shortest paths back to their own spawn.
    """

    def __init__(self, maze: Maze, rng: Random | None = None) -> None:
        """Store the maze and an independent optional random generator."""
        self.maze = maze
        self.rng = rng if rng is not None else Random()

    def _open(self, cell: Cell) -> bool:
        """Return whether a tile is inside the maze and traversable."""
        return self.maze.in_bounds(*cell) and not self.maze.is_wall(*cell)

    def legal_moves(self, cell: Cell) -> dict[Direction, Cell]:
        """Return legal neighboring tiles keyed by movement direction."""
        if not self._open(cell):
            return {}
        x, y = cell
        return {
            direction: (x + dx, y + dy)
            for direction, (dx, dy) in STEPS.items()
            if self._open((x + dx, y + dy))
        }

    def _distances(self, target: Cell) -> dict[Cell, int]:
        """Measure shortest corridor distances from a target using BFS."""
        if not self._open(target):
            return {}
        distances = {target: 0}
        queue: deque[Cell] = deque([target])
        while queue:
            cell = queue.popleft()
            for neighbor in self.legal_moves(cell).values():
                if neighbor not in distances:
                    distances[neighbor] = distances[cell] + 1
                    queue.append(neighbor)
        return distances

    def _shortest(
        self, moves: dict[Direction, Cell], target: Cell,
    ) -> Direction | None:
        """Choose a random tie among neighbors on shortest paths."""
        distances = self._distances(target)
        reachable = {
            direction: distances[cell]
            for direction, cell in moves.items() if cell in distances
        }
        if not reachable:
            return None
        best = min(reachable.values())
        return self.rng.choice([
            direction for direction, distance in reachable.items()
            if distance == best
        ])

    def _greedy(
        self, moves: dict[Direction, Cell], target: Cell,
    ) -> Direction:
        """Choose by Manhattan distance, without searching around walls."""
        distances = {
            direction: abs(cell[0] - target[0]) + abs(cell[1] - target[1])
            for direction, cell in moves.items()
        }
        best = min(distances.values())
        return self.rng.choice([
            direction for direction, distance in distances.items()
            if distance == best
        ])

    def choose_direction(
        self,
        color: GhostColor,
        cell: Cell,
        current_direction: Direction,
        player_cell: Cell,
        player_direction: Direction,
        mode: GhostMode = "normal",
        home: Cell | None = None,
    ) -> Direction | None:
        """Choose one legal tile step, or None if no movement is possible.

        Args:
            color: Ghost personality.
            cell: Current integer tile center of the ghost.
            current_direction: Direction used to reach this center.
            player_cell: Traversable tile occupied by the player.
            player_direction: Current player movement direction.
            mode: Normal pursuit, frightened flight, or eaten return.
            home: Ghost spawn tile, required in eaten mode.

        Raises:
            ValueError: If a color, direction or mode is invalid, or
                eaten mode is requested without a home tile.
        """
        if color not in ("red", "pink", "blue", "yellow"):
            raise ValueError(f"Unknown ghost color: {color}")
        if current_direction not in STEPS or player_direction not in STEPS:
            raise ValueError("Unknown movement direction.")
        if mode not in ("normal", "frightened", "eaten"):
            raise ValueError(f"Unknown ghost mode: {mode}")
        if mode == "eaten" and home is None:
            raise ValueError("Eaten ghosts require a home tile.")

        moves = self.legal_moves(cell)
        if not moves:
            return None
        if mode == "eaten":
            if home is None or cell == home:
                return None
            return self._shortest(moves, home)
        if mode == "frightened":
            distances = self._distances(player_cell)
            reachable = {
                direction: distances[tile]
                for direction, tile in moves.items() if tile in distances
            }
            if not reachable:
                return self.rng.choice(list(moves))
            farthest = max(reachable.values())
            return self.rng.choice([
                direction for direction, distance in reachable.items()
                if distance == farthest
            ])
        if color == "red":
            return self._shortest(moves, player_cell)

        # Avoid immediate backtracking when another exit is available.
        if len(moves) > 1:
            moves.pop(OPPOSITE[current_direction], None)
        if len(moves) == 1:
            return next(iter(moves))
        chance = 0.80 if color == "yellow" else 0.35
        if color in ("blue", "yellow") and self.rng.random() < chance:
            return self.rng.choice(list(moves))
        target = player_cell
        if color == "pink":
            # Look ahead only through open tiles, so the target is valid.
            dx, dy = STEPS[player_direction]
            for _ in range(4):
                ahead = (target[0] + dx, target[1] + dy)
                if not self._open(ahead):
                    break
                target = ahead
        return self._greedy(moves, target)
