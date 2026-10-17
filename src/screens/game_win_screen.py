"""Display the victory screen after completing the maze."""

from collections.abc import Callable

import pygame

from src.screens.base_screen import BaseScreen


class GameWinScreen(BaseScreen):
    """Show the winning score and navigation buttons."""

    def __init__(
        self,
        surface: pygame.Surface,
        change_screen: Callable[[str], None],
        score: int = 0,
    ) -> None:
        """Prepare the victory layout and navigation."""
        super().__init__(surface)

        self.change_screen = change_screen
        self.score = score
        self._leaving = False

        self.width, self.height = surface.get_size()

        scale = min(
            self.width / 1200,
            self.height / 800,
        )

        self.title_font = pygame.font.Font(
            None,
            max(20, round(100 * scale)),
        )
        self.score_font = pygame.font.Font(
            None,
            max(16, round(50 * scale)),
        )
        self.button_font = pygame.font.Font(
            None,
            max(14, round(40 * scale)),
        )

        width = max(1, round(320 * scale))
        height = max(1, round(65 * scale))
        x = (self.width - width) // 2

        self.play_again_rect = pygame.Rect(
            x,
            round(self.height * 470 / 800),
            width,
            height,
        )
        self.menu_rect = pygame.Rect(
            x,
            round(self.height * 550 / 800),
            width,
            height,
        )
        self.quit_rect = pygame.Rect(
            x,
            round(self.height * 630 / 800),
            width,
            height,
        )

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle keyboard shortcuts and navigation buttons."""
        if self._leaving:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self._navigate("gameplay")
            elif event.key == pygame.K_ESCAPE:
                self._navigate("menu")

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button != 1:
                return

            if self.play_again_rect.collidepoint(event.pos):
                self._navigate("gameplay")

            elif self.menu_rect.collidepoint(event.pos):
                self._navigate("menu")

            elif self.quit_rect.collidepoint(event.pos):
                self._leaving = True
                pygame.event.post(
                    pygame.event.Event(pygame.QUIT)
                )

    def update(self, dt: float) -> None:
        """Keep the completed score fixed."""
        _ = dt

    def render(self) -> None:
        """Draw the victory background, final score and buttons."""
        self.surface.fill((8, 12, 28))

        overlay = pygame.Surface(
            self.surface.get_size(),
            pygame.SRCALPHA,
        )

        center = (
            self.width // 2,
            round(self.height * 0.30),
        )
        radius = max(
            1,
            round(min(self.width, self.height) * 0.325),
        )

        pygame.draw.circle(
            overlay,
            (255, 210, 50, 20),
            center,
            radius,
        )
        pygame.draw.circle(
            overlay,
            (255, 225, 100, 30),
            center,
            max(1, radius * 9 // 13),
        )

        self.surface.blit(overlay, (0, 0))

        self._draw_center_text(
            "YOU WIN!",
            self.title_font,
            round(self.height * 0.25),
            (255, 220, 100),
        )
        self._draw_center_text(
            f"SCORE: {self.score}",
            self.score_font,
            round(self.height * 330 / 800),
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

    def _navigate(self, destination: str) -> None:
        """Switch screens once per activation."""
        if self._leaving:
            return

        self._leaving = True
        self.change_screen(destination)

    def _draw_center_text(
        self,
        text: str,
        font: pygame.font.Font,
        y: int,
        color: tuple[int, int, int],
    ) -> None:
        """Draw text centered horizontally."""
        image = font.render(
            text,
            True,
            color,
        )
        rect = image.get_rect(
            center=(self.width // 2, y),
        )

        self.surface.blit(image, rect)

    def _draw_button(
        self,
        rect: pygame.Rect,
        text: str,
    ) -> None:
        """Draw a button with a mouse-hover highlight."""
        hovered = rect.collidepoint(
            pygame.mouse.get_pos()
        )

        background = (
            (110, 85, 30)
            if hovered
            else (45, 40, 35)
        )
        border = (
            (255, 225, 120)
            if hovered
            else (160, 135, 65)
        )

        pygame.draw.rect(
            self.surface,
            background,
            rect,
            border_radius=14,
        )
        pygame.draw.rect(
            self.surface,
            border,
            rect,
            width=3,
            border_radius=14,
        )

        image = self.button_font.render(
            text,
            True,
            (255, 255, 255),
        )
        self.surface.blit(
            image,
            image.get_rect(center=rect.center),
        )
