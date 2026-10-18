"""Show victory or defeat over the final maze and save a named score."""

from collections.abc import Callable
from pathlib import Path

import pygame

from src.managers.score_manager import add_score, load_scores
from src.screens.base_screen import BaseScreen


class ResultScreen(BaseScreen):
    """Freeze the finished maze behind a result and name-entry panel."""

    def __init__(
        self, surface: pygame.Surface, change_screen: Callable[[str], None],
        score: int, won: bool, background: pygame.Surface | None,
        theme_name: str,
    ) -> None:
        """Prepare a snapshot, theme colors and editable player name."""
        super().__init__(surface)
        self.change_screen = change_screen
        self.score = score
        self.won = won
        self.name = ""
        self.saved = False
        self.error = ""
        self.scores = load_scores()
        self.accent = (
            (130, 225, 255) if theme_name == "ice" else (210, 150, 255)
        )
        self.background = pygame.Surface(surface.get_size())
        self.background.fill((4, 8, 20))
        if background is not None:
            # Fit the whole final maze without distorting its proportions.
            fitted = pygame.transform.smoothscale_by(
                background, min(
                    surface.get_width() / background.get_width(),
                    surface.get_height() / background.get_height(),
                ),
            )
            self.background.blit(
                fitted, fitted.get_rect(center=surface.get_rect().center),
            )
        shade = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        shade.fill((1, 3, 15, 155))
        self.background.blit(shade, (0, 0))
        theme = "cosmic" if theme_name == "cosmic" else "ice"
        image_path = (
            Path("images") / "maze" / theme / "win_screen.png" if won
            else Path("images") / f"gameover_{theme}.png"
        )
        self.result_image: pygame.Surface | None = None
        try:
            source = pygame.image.load(str(image_path)).convert_alpha()
            bounds = source.get_bounding_rect(min_alpha=8)
            if bounds.width and bounds.height:
                source = source.subsurface(bounds).copy()
                factor = min(560 / source.get_width(),
                             280 / source.get_height())
                self.result_image = pygame.transform.smoothscale(source, (
                    max(1, round(source.get_width() * factor)),
                    max(1, round(source.get_height() * factor)),
                ))
        except (OSError, pygame.error):
            # Keep name entry accessible even if an asset is unavailable.
            self.result_image = None
        self.title_font = pygame.font.Font(None, 78)
        self.font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 25)
        cx = surface.get_width() // 2
        cy = surface.get_height() // 2
        self.panel = pygame.Rect(cx - 300, cy - 370, 600, 740)
        self.input_rect = pygame.Rect(cx - 210, cy - 4, 420, 48)
        self.save_rect = pygame.Rect(cx - 210, cy + 60, 420, 46)
        self.menu_rect = pygame.Rect(cx - 210, cy + 302, 420, 46)

    def _save(self) -> None:
        """Save once, retaining the form if validation or writing fails."""
        if self.saved:
            return
        try:
            add_score(self.name, self.score)
        except ValueError as error:
            self.error = str(error)
            return
        except OSError:
            self.error = "Could not save. Check file permissions and retry."
            return
        self.saved = True
        self.error = ""
        self.scores = load_scores()

    def handle_event(self, event: pygame.event.Event) -> None:
        """Edit the name, save with Enter, and return after saving."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.saved:
                    self.change_screen("menu")
                else:
                    self._save()
            elif event.key == pygame.K_BACKSPACE and not self.saved:
                self.name = self.name[:-1]
            elif not self.saved:
                text = getattr(event, "unicode", "")
                self.name = (self.name + "".join(
                    char for char in text if char.isalnum() or char == " "
                ))[:10]
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.save_rect.collidepoint(event.pos):
                self._save()
            elif self.saved and self.menu_rect.collidepoint(event.pos):
                self.change_screen("menu")

    def update(self, dt: float) -> None:
        """Keep the completed game snapshot still."""

    def _text(
        self, text: str, y: int, color: tuple[int, int, int],
        font: pygame.font.Font | None = None,
    ) -> None:
        """Center a line inside the result panel."""
        image = (font or self.font).render(text, True, color)
        self.surface.blit(image, image.get_rect(
            center=(self.surface.get_width() // 2, y),
        ))

    def render(self) -> None:
        """Draw the result, name form and leading saved scores below."""
        self.surface.blit(self.background, (0, 0))
        panel = pygame.Surface(self.panel.size, pygame.SRCALPHA)
        panel.fill((5, 10, 28, 220))
        self.surface.blit(panel, self.panel)
        pygame.draw.rect(
            self.surface, self.accent, self.panel, 2, border_radius=20,
        )
        cy = self.surface.get_height() // 2
        white = (240, 245, 255)
        title_color = (255, 220, 95) if self.won else (255, 135, 155)
        if self.result_image is not None:
            self.surface.blit(self.result_image, self.result_image.get_rect(
                center=(self.surface.get_width() // 2, cy - 210),
            ))
        else:
            self._text(
                "YOU WIN!" if self.won else "GAME OVER", cy - 210,
                title_color, self.title_font,
            )
        self._text(f"YOUR SCORE: {self.score:,}", cy - 52, white)
        self._text("ENTER YOUR NAME (MAX 10)", cy - 22,
                   self.accent, self.small_font)
        pygame.draw.rect(self.surface, (12, 23, 45), self.input_rect,
                         border_radius=8)
        pygame.draw.rect(self.surface, self.accent, self.input_rect, 2,
                         border_radius=8)
        self._text(self.name or "_", self.input_rect.centery, white)
        pygame.draw.rect(self.surface, (30, 55, 85), self.save_rect,
                         border_radius=8)
        self._text("SAVED" if self.saved else "SAVE SCORE / ENTER",
                   self.save_rect.centery, self.accent)
        if self.error:
            self._text(self.error, cy + 123, (255, 160, 160), self.small_font)
        self._text("HIGH SCORES", cy + 155, self.accent)
        if not self.scores:
            self._text("NO SCORES YET", cy + 204, white, self.small_font)
        for index, entry in enumerate(self.scores[:3]):
            self._text(
                f"{index + 1}.  {entry['name']}    {entry['score']:,}",
                cy + 192 + index * 30, white, self.small_font,
            )
        self._text("Full top 10: Main Menu > High Scores", cy + 281,
                   self.accent, self.small_font)
        pygame.draw.rect(self.surface, (30, 55, 85), self.menu_rect,
                         border_radius=8)
        self._text("BACK TO MENU" if self.saved else "SAVE TO CONTINUE",
                   self.menu_rect.centery, white)
