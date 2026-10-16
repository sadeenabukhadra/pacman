class GameStatus:
    def __init__(
        self,
        lives: int,
        level: int = 1,
        score: int = 0,
    ) -> None:
        self.lives = lives
        self.level = level
        self.score = score

        self.paused = False
        self.game_over = False
        self.victory = False

    def add_score(self, points: int) -> None:
        self.score += points

    def lose_life(self) -> None:
        if self.lives > 0:
            self.lives -= 1

        if self.lives == 0:
            self.game_over = True

    def next_level(self) -> None:
        self.level += 1

    def pause(self) -> None:
        self.paused = True

    def resume(self) -> None:
        self.paused = False

    def set_victory(self) -> None:
        self.victory = True

    def reset(
        self,
        lives: int,
    ) -> None:
        self.lives = lives
        self.level = 1
        self.score = 0

        self.paused = False
        self.game_over = False
        self.victory = False