"""Provide the high scores screen."""

from collections.abc import Callable
from pathlib import Path

import pygame

from src.managers.score_manager import load_scores
from src.screens.base_screen import BaseScreen
from src.ui.button import Button

REF_W = 1536
REF_BUTTON_W, REF_BUTTON_H = 410, 74
REF_FONT_SIZE = 32
REF_ROW_FONT_SIZE = 30

REF_RANK_X = 470
REF_NAME_X = 560
REF_SCORE_X = 1070
REF_FIRST_ROW_Y = 300
REF_ROW_STEP = 52
REF_BACK_CY = 940

TEXT_COLOR = (235, 245, 255)
TOP_COLOR = (170, 245, 255)
EMPTY_COLOR = (170, 215, 255)


def _load_font(path: str, size: int) -> pygame.font.Font:
    """Load a TTF font, or fall back to the default font."""
    font_file = Path(path)
    if font_file.exists():
        return pygame.font.Font(str(font_file), size)
    return pygame.font.Font(None, round(size * 1.4))


class HighScoresScreen(BaseScreen):
    """Display the best scores with a back button."""

    def __init__(
        self,
        surface: pygame.Surface,
        change_screen: Callable[[str], None],
    ) -> None:
        """Initialize the high scores screen."""
        super().__init__(surface)
        self.change_screen = change_screen

        width, height = self.surface.get_size()
        self.scale = width / REF_W

        self.background = pygame.transform.smoothscale(
            pygame.image.load("images/high_scores.jpeg").convert(),
            (width, height),
        )

        self.row_font = _load_font(
            "fonts/orbitron-semibold.ttf",
            round(REF_ROW_FONT_SIZE * self.scale),
        )
        button_font = _load_font(
            "fonts/orbitron-semibold.ttf",
            round(REF_FONT_SIZE * self.scale * 0.8),
        )

        rect = pygame.Rect(
            0,
            0,
            round(REF_BUTTON_W * self.scale * 0.8),
            round(REF_BUTTON_H * self.scale * 0.8),
        )
        rect.center = (width // 2, round(REF_BACK_CY * self.scale))

        self.back_button = Button(
            rect=rect,
            text="BACK TO MENU",
            font=button_font,
            normal_image=pygame.image.load(
                "images/main_menu/option.png"
            ).convert_alpha(),
            selected_image=pygame.image.load(
                "images/main_menu/select.png"
            ).convert_alpha(),
            star_image=pygame.image.load(
                "images/main_menu/star_select.png"
            ).convert_alpha(),
        )
        self.back_button.set_selected(True)

        self.scores = load_scores()

    def _go_back(self) -> None:
        """Return to the main menu."""
        self.change_screen("menu")

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle input."""
        if event.type == pygame.KEYDOWN:
            if event.key in (
                pygame.K_ESCAPE,
                pygame.K_RETURN,
                pygame.K_BACKSPACE,
            ):
                self._go_back()

        elif (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.back_button.is_hovered(event.pos)
        ):
            self._go_back()

    def update(self, dt: float) -> None:
        """Update the screen."""

    def _draw_text(
        self,
        text: str,
        color: tuple[int, int, int],
        ref_x: int,
        ref_y: int,
        align: str,
    ) -> None:
        """Draw one text item aligned on a reference position."""
        text_surface = self.row_font.render(text, True, color)
        position = (
            round(ref_x * self.scale),
            round(ref_y * self.scale),
        )
        rect = text_surface.get_rect(**{align: position})
        self.surface.blit(text_surface, rect)

    def render(self) -> None:
        """Draw the screen."""
        self.surface.blit(self.background, (0, 0))

        if not self.scores:
            self._draw_text(
                "NO SCORES YET",
                EMPTY_COLOR,
                REF_W // 2,
                REF_FIRST_ROW_Y + 4 * REF_ROW_STEP,
                "center",
            )
        else:
            for index, entry in enumerate(self.scores):
                y = REF_FIRST_ROW_Y + index * REF_ROW_STEP
                color = TOP_COLOR if index == 0 else TEXT_COLOR

                self._draw_text(f"{index + 1}.", color, REF_RANK_X, y, "midright")
                self._draw_text(entry["name"], color, REF_NAME_X, y, "midleft")
                self._draw_text(
                    f"{entry['score']:,}", color, REF_SCORE_X, y, "midright"
                )

        self.back_button.render(self.surface)