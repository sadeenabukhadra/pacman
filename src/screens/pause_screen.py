"""Draw a themed pause overlay above the existing gameplay screen."""

from collections.abc import Callable
from pathlib import Path

import pygame

from src.managers.asset_manager import AssetManager
from src.screens.base_screen import BaseScreen
from src.themes.theme_manager import ThemeManager


class PauseScreen(BaseScreen):
    """Display pause controls without owning or recreating game state.

    Gameplay should stop updating while this overlay is open, render
    its frozen scene first, then call this overlay's render method.
    Resume and menu callbacks are supplied by gameplay integration.
    """

    def __init__(
        self,
        surface: pygame.Surface,
        theme_manager: ThemeManager,
        asset_manager: AssetManager,
        on_resume: Callable[[], None],
        on_restart: Callable[[], None],
        on_main_menu: Callable[[], None],
    ) -> None:
        """Prepare themed panel images and mouse/keyboard controls.

        Args:
            surface: Display surface shared with gameplay.
            theme_manager: Source of the active ice or cosmic theme.
            asset_manager: Shared image loader and cache.
            on_resume: Callback that closes the overlay, keeping the game.
            on_restart: Callback that starts a fresh game from level one.
            on_main_menu: Callback that returns to the main menu.
        """
        super().__init__(surface)
        self.on_resume = on_resume
        self.on_restart = on_restart
        self.on_main_menu = on_main_menu
        self.selected_index = 0
        self._closing = False
        name = theme_manager.current.name
        self.theme_name = name if name in ("ice", "cosmic") else "ice"
        root = f"maze/{self.theme_name}/puse"
        page = self._trim(asset_manager.load(f"{root}/page_puse.png"))
        normal = self._trim(asset_manager.load(f"{root}/optional.png"))
        selected = self._trim(
            asset_manager.load(f"{root}/select_option.png"),
        )
        width, height = surface.get_size()
        scale = min(width / 1200, height / 800)
        max_width = max(1, round(width * 0.60))
        max_height = max(1, round(height * 0.84))
        ratio = min(
            max_width / page.get_width(), max_height / page.get_height(),
        )
        panel_size = (
            max(1, round(page.get_width() * ratio)),
            max(1, round(page.get_height() * ratio)),
        )
        self.panel = pygame.transform.smoothscale(page, panel_size)
        self.panel_rect = self.panel.get_rect(center=(width // 2, height // 2))
        self.shade = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        self.shade.fill((0, 0, 12, 170))

        button_width = max(1, round(self.panel_rect.width * 0.70))
        button_height = max(1, round(self.panel_rect.height * 0.12))
        self.normal_image = pygame.transform.smoothscale(
            normal, (button_width, button_height),
        )
        self.selected_image = pygame.transform.smoothscale(
            selected, (button_width, button_height),
        )
        self.buttons: list[pygame.Rect] = []
        for fraction in (0.50, 0.66, 0.82):
            rect = pygame.Rect(0, 0, button_width, button_height)
            rect.center = (
                self.panel_rect.centerx,
                self.panel_rect.top + round(self.panel_rect.height * fraction),
            )
            self.buttons.append(rect)
        font_path = (
            Path(__file__).resolve().parents[2]
            / "fonts" / "orbitron-semibold.ttf"
        )
        font_file = str(font_path) if font_path.is_file() else None
        font_size = min(round(27 * scale), round(button_height * 0.45))
        if font_file is None:
            font_size = round(font_size * 1.35)
        self.font = pygame.font.Font(font_file, max(8, font_size))
        self.help_font = pygame.font.Font(None, max(10, round(23 * scale)))
        self.labels = ("RESUME", "RESTART GAME", "MAIN MENU")

    @staticmethod
    def _trim(image: pygame.Surface) -> pygame.Surface:
        """Remove transparent outer padding from an image when present."""
        bounds = image.get_bounding_rect(min_alpha=32)
        if bounds.width == 0 or bounds.height == 0:
            return image
        return image.subsurface(bounds).copy()

    def _activate(self, index: int) -> None:
        """Run one callback, ignoring further events after navigation."""
        if self._closing:
            return
        self._closing = True
        if index == 0:
            self.on_resume()
        elif index == 1:
            self.on_restart()
        else:
            self.on_main_menu()

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle arrows, Enter, Space, Escape, P and mouse interaction."""
        if self._closing:
            return
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_p):
                self._activate(0)
            elif event.key == pygame.K_UP:
                self.selected_index = (
                    self.selected_index - 1
                ) % len(self.labels)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (
                    self.selected_index + 1
                ) % len(self.labels)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._activate(self.selected_index)
        elif event.type == pygame.MOUSEMOTION:
            for index, rect in enumerate(self.buttons):
                if rect.collidepoint(event.pos):
                    self.selected_index = index
                    break
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for index, rect in enumerate(self.buttons):
                if rect.collidepoint(event.pos):
                    self.selected_index = index
                    self._activate(index)
                    break

    def update(self, dt: float) -> None:
        """Keep the overlay static; gameplay owns all simulation timers."""

    def render(self) -> None:
        """Dim the frozen game and draw the themed panel and controls."""
        self.surface.blit(self.shade, (0, 0))
        self.surface.blit(self.panel, self.panel_rect)
        for index, rect in enumerate(self.buttons):
            selected = index == self.selected_index
            image = self.selected_image if selected else self.normal_image
            self.surface.blit(image, rect)
            color = (255, 255, 255) if selected else (205, 225, 245)
            text = self.font.render(self.labels[index], True, color)
            if text.get_width() > rect.width * 0.8:
                ratio = rect.width * 0.8 / text.get_width()
                text = pygame.transform.smoothscale(text, (
                    max(1, round(text.get_width() * ratio)),
                    max(1, round(text.get_height() * ratio)),
                ))
            self.surface.blit(text, text.get_rect(center=rect.center))
        hint = self.help_font.render(
            "ESC / P: RESUME    ENTER: CONFIRM", True, (220, 230, 245),
        )
        center = (
            self.surface.get_width() // 2,
            min(self.surface.get_height() - hint.get_height(),
                self.panel_rect.bottom + hint.get_height()),
        )
        self.surface.blit(hint, hint.get_rect(center=center))
