import pygame

from src.core.game import Game


class GameLoop:
    def __init__(
        self,
        game: Game,
        fps: int = 60,
    ) -> None:
        self.game = game
        self.fps = fps
        self.clock = pygame.time.Clock()

    def run(self) -> None:
        while self.game.is_running():
            self.handle_events()
            self.update()
            self.render()

            self.clock.tick(self.fps)

    def handle_events(self) -> None:
        for event in pygame.event.get():
            self.game.handle_event(event)

    def update(self) -> None:
        self.game.update()

    def render(self) -> None:
        pygame.display.flip()