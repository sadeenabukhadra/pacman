"""Game over screen for the Pac-Man game."""

from collections.abc import Callable

import pygame

from src.screens.base_screen import BaseScreen


class GameOverScreen(BaseScreen):
    """Display the game over screen when the player loses all lives."""

    def __init__(
        self,
        surface: pygame.Surface,
        change_screen: Callable[[str], None],
        score: int = 0,
    ) -> None:
        """Initialize the game over screen.

        Args:
            surface: Main pygame display surface.
            change_screen: Callback used to switch screens.
            score: Final score of the player.
        """
        super().__init__(surface)

        self.change_screen = change_screen
        self.score = score

        self.width = self.surface.get_width()
        self.height = self.surface.get_height()

        self.title_font = pygame.font.Font(None, 100)
        self.score_font = pygame.font.Font(None, 50)
        self.button_font = pygame.font.Font(None, 40)

        button_width = 320
        button_height = 65

        center_x = (self.width - button_width) // 2

        self.play_again_rect = pygame.Rect(
            center_x,
            470,
            button_width,
            button_height,
        )

        self.menu_rect = pygame.Rect(
            center_x,
            550,
            button_width,
            button_height,
        )

        self.quit_rect = pygame.Rect(
            center_x,
            630,
            button_width,
            button_height,
        )

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle keyboard and mouse events.

        Args:
            event: Current pygame event.
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self._play_again()

            elif event.key == pygame.K_ESCAPE:
                self._main_menu()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button != 1:
                return

            mouse_pos = event.pos

            if self.play_again_rect.collidepoint(mouse_pos):
                self._play_again()

            elif self.menu_rect.collidepoint(mouse_pos):
                self._main_menu()

            elif self.quit_rect.collidepoint(mouse_pos):
                pygame.event.post(
                    pygame.event.Event(pygame.QUIT)
                )

    def update(self, dt: float) -> None:
        """Update the game over screen.

        Args:
            dt: Time elapsed since the previous frame.
        """
        _ = dt

    def render(self) -> None:
        """Draw the game over screen."""
        self._draw_background()

        self._draw_center_text(
            "GAME OVER",
            self.title_font,
            200,
            (255, 80, 80),
        )

        self._draw_center_text(
            f"SCORE: {self.score}",
            self.score_font,
            330,
            (235, 245, 255),
        )

        self._draw_button(
            self.play_again_rect,
            "PLAY AGAIN",
        )

        self._draw_button(
            self.menu_rect,
            "MAIN MENU",
        )

        self._draw_button(
            self.quit_rect,
            "QUIT GAME",
        )

    def _draw_background(self) -> None:
        """Draw the game over background."""
        self.surface.fill((8, 12, 28))

        overlay = pygame.Surface(
            (self.width, self.height),
            pygame.SRCALPHA,
        )

        pygame.draw.circle(
            overlay,
            (255, 30, 30, 25),
            (self.width // 2, 240),
            260,
        )

        pygame.draw.circle(
            overlay,
            (180, 20, 20, 20),
            (self.width // 2, 240),
            180,
        )

        self.surface.blit(overlay, (0, 0))

    def _draw_center_text(
        self,
        text: str,
        font: pygame.font.Font,
        y: int,
        color: tuple[int, int, int],
    ) -> None:
        """Draw centered text.

        Args:
            text: Text to render.
            font: Font used to render the text.
            y: Vertical center position.
            color: Text color.
        """
        text_surface = font.render(
            text,
            True,
            color,
        )

        text_rect = text_surface.get_rect(
            center=(self.width // 2, y),
        )

        self.surface.blit(
            text_surface,
            text_rect,
        )

    def _draw_button(
        self,
        rect: pygame.Rect,
        text: str,
    ) -> None:
        """Draw a button.

        Args:
            rect: Button rectangle.
            text: Button text.
        """
        mouse_pos = pygame.mouse.get_pos()

        if rect.collidepoint(mouse_pos):
            background_color = (150, 45, 55)
            border_color = (255, 130, 130)
        else:
            background_color = (75, 35, 55)
            border_color = (180, 70, 90)

        pygame.draw.rect(
            self.surface,
            background_color,
            rect,
            border_radius=14,
        )

        pygame.draw.rect(
            self.surface,
            border_color,
            rect,
            width=3,
            border_radius=14,
        )

        text_surface = self.button_font.render(
            text,
            True,
            (255, 255, 255),
        )

        text_rect = text_surface.get_rect(
            center=rect.center,
        )

        self.surface.blit(
            text_surface,
            text_rect,
        )

    def _play_again(self) -> None:
        """Restart the game."""
        self.change_screen("gameplay")

    def _main_menu(self) -> None:
        """Return to the main menu."""
        self.change_screen("menu")
