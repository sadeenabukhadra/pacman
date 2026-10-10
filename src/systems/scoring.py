from src.core import GameStatus


class ScoringSystem:
    def __init__(
        self,
        game_status: GameStatus,
        pellet_points: int,
        power_crystal_points: int,
        ghost_points: int,
    ) -> None:
        self.game_status = game_status

        self.pellet_points = pellet_points
        self.power_crystal_points = power_crystal_points
        self.ghost_points = ghost_points

    def add_pellet_score(self) -> None:
        self.game_status.add_score(
            self.pellet_points,
        )

    def add_power_crystal_score(self) -> None:
        self.game_status.add_score(
            self.power_crystal_points,
        )

    def add_ghost_score(self) -> None:
        self.game_status.add_score(
            self.ghost_points,
        )

    def get_score(self) -> int:
        return self.game_status.score