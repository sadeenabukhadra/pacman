"""Represent an ordinary Pac-Man pellet independently of its sprite."""

from dataclasses import dataclass, field


@dataclass
class Pellet:
    """Store one collectible's tile position, score and consumed state.

    Tile coordinates match Maze, Pacman and MazeRenderer. Image loading
    and collision detection belong to rendering and gameplay systems.
    """

    x: int
    y: int
    points: int = 10
    eaten: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        """Reject invalid coordinates and scores.

        Raises:
            ValueError: If coordinates or points are not non-negative ints.
        """
        for name, value in (
            ("x", self.x), ("y", self.y), ("points", self.points),
        ):
            if type(value) is not int or value < 0:
                raise ValueError(f"Pellet {name} must be a non-negative int.")

    @property
    def position(self) -> tuple[int, int]:
        """Return the expanded maze tile containing this pellet."""
        return self.x, self.y

    @property
    def is_super(self) -> bool:
        """Return False for an ordinary pellet."""
        return False

    def consume(self) -> bool:
        """Mark the pellet eaten exactly once and report success.

        Returns:
            True on first consumption; False if already eaten. Award
            points only when this method returns True.
        """
        if self.eaten:
            return False
        self.eaten = True
        return True