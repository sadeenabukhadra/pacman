"""Provide the main menu screen of the game."""

from collections.abc import Callable
from pathlib import Path

import pygame

from src.screens.base_screen import BaseScreen
from src.ui.button import Button

# قياسات التصميم المرجعي (main_menu.jpeg)
REF_W, REF_H = 1536, 1024
REF_BUTTON_W, REF_BUTTON_H = 410, 74
REF_STEP = 86                      # المسافة بين مركزَي زرين
REF_CENTER_X, REF_FIRST_CY = 1173, 373          
REF_FONT_SIZE = 32
REF_HELP_FONT_SIZE = 22
REF_HELP_Y = (790, 822)

HELP_COLOR = (170, 215, 255)


def _load_font(
    path: str,
    size: int,
    fallback_scale: float = 1.4,
) -> pygame.font.Font:
    """Load a TTF font, or fall back to the default font."""
    font_file = Path(path)
    if font_file.exists():
        return pygame.font.Font(str(font_file), size)
    return pygame.font.Font(None, round(size * fallback_scale))


class MenuScreen(BaseScreen):
    """Display and control the main menu."""

    def __init__(
        self,
        surface: pygame.Surface,
        change_screen: Callable[[str], None],
    ) -> None:
        """Initialize the main menu."""
        super().__init__(surface)

        self.change_screen = change_screen
        self.selected_index = 0

        width, height = self.surface.get_size()
        self.scale = width / REF_W

        # -------------------------
        # Background
        # -------------------------

        self.background = pygame.image.load(
        "images/main_menu/menu.png"
        ).convert()

        self.background = pygame.transform.smoothscale(
            self.background,
            (width, height),
        )

        # -------------------------
        # Button images
        # -------------------------

        self.option_image = pygame.image.load(
            "images/main_menu/option.png"
        ).convert_alpha()

        self.select_image = pygame.image.load(
            "images/main_menu/select.png"
        ).convert_alpha()

        self.star_image = pygame.image.load(
            "images/main_menu/star_select.png"
        ).convert_alpha()

        # -------------------------
        # Fonts
        # -------------------------

        self.font = _load_font(
            "fonts/orbitron-semibold.ttf",
            round(REF_FONT_SIZE * self.scale),
        )
        help_font = _load_font(
            "fonts/orbitron-regular.ttf",
            round(REF_HELP_FONT_SIZE * self.scale),
        )

        # -------------------------
        # Help text
        # -------------------------

        self.help_center_x = round(REF_CENTER_X * self.scale)
        self.help_lines = [
            (
                help_font.render("UP / DOWN: SELECT", True, HELP_COLOR),
                round(REF_HELP_Y[0] * self.scale),
            ),
            (
                help_font.render("ENTER: CONFIRM", True, HELP_COLOR),
                round(REF_HELP_Y[1] * self.scale),
            ),
        ]

        # -------------------------
        # Buttons
        # -------------------------

        self.buttons: list[Button] = []

        buttons_texts = [
            "START GAME",
            "INSTRUCTIONS",
            "HIGH SCORES",
            "SETTINGS",
            "QUIT GAME",
        ]

        button_width = round(REF_BUTTON_W * self.scale)
        button_height = round(REF_BUTTON_H * self.scale)
        step = round(REF_STEP * self.scale)

        center_x = round(REF_CENTER_X * self.scale)
        first_cy = round(REF_FIRST_CY * self.scale)

        for index, text in enumerate(buttons_texts):
            rect = pygame.Rect(0, 0, button_width, button_height)
            rect.center = (center_x, first_cy + index * step)

            self.buttons.append(
                Button(
                    rect=rect,
                    text=text,
                    font=self.font,
                    normal_image=self.option_image,
                    selected_image=self.select_image,
                    star_image=self.star_image,
                )
            )

        self._update_selection()

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle menu input."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.selected_index = (
                    self.selected_index + 1
                ) % len(self.buttons)
                self._update_selection()

            elif event.key == pygame.K_UP:
                self.selected_index = (
                    self.selected_index - 1
                ) % len(self.buttons)
                self._update_selection()

            elif event.key == pygame.K_RETURN:
                self._activate_selected_button()

        elif event.type == pygame.MOUSEMOTION:
            for index, button in enumerate(self.buttons):
                if button.is_hovered(event.pos):
                    self.selected_index = index
                    self._update_selection()
                    break

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for index, button in enumerate(self.buttons):
                    if button.is_hovered(event.pos):
                        self.selected_index = index
                        self._update_selection()
                        self._activate_selected_button()
                        break

    def _update_selection(self) -> None:
        """Update selected button."""
        for index, button in enumerate(self.buttons):
            button.set_selected(index == self.selected_index)

    def _activate_selected_button(self) -> None:
        """Activate selected menu option."""
        if self.selected_index == 0:
            self.change_screen("gameplay")

        elif self.selected_index == 1:
            self.change_screen("instructions")

        elif self.selected_index == 2:
            self.change_screen("high_scores")

        elif self.selected_index == 3:
            self.change_screen("settings")

        elif self.selected_index == 4:
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def update(self, dt: float) -> None:
        """Update menu."""

    def render(self) -> None:
        """Draw menu."""
        self.surface.blit(self.background, (0, 0))

        for button in self.buttons:
            button.render(self.surface)

        for text_surface, y in self.help_lines:
            self.surface.blit(
                text_surface,
                text_surface.get_rect(center=(self.help_center_x, y)),
            )