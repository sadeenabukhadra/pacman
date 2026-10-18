"""Draw a themed gameplay HUD without changing game state."""

import math
from pathlib import Path

import pygame

from src.managers.asset_manager import AssetManager
from src.themes.theme_manager import ThemeManager


class HUD:
    """Display level, score, remaining time and lives above the maze.

    The gameplay screen must reserve self.height pixels at the top of
    the window for this HUD. Values are supplied anew on every render.
    """

    PANEL_PATHS = {
        "ice": "maze/ice/hud_ice.png",
        "cosmic": "maze/cosmic/hud_panel.png",
    }
    LABELS = ("LEVEL", "SCORE", "TIME", "LIVES")

    def __init__(
        self,
        surface: pygame.Surface,
        asset_manager: AssetManager,
        theme_manager: ThemeManager,
        height: int = 130,
    ) -> None:
        """Prepare HUD placement and fonts.

        Args:
            surface: Display surface shared with the maze renderer.
            asset_manager: Shared image loader and cache.
            theme_manager: Source of the selected theme.
            height: Total top area, including the panel's outer padding.

        Raises:
            ValueError: If the HUD cannot fit inside the surface.
        """
        if height < 60 or height >= surface.get_height():
            raise ValueError("HUD height must fit inside the game window.")
        self.surface = surface
        self.asset_manager = asset_manager
        self.theme_manager = theme_manager
        self.height = height
        self._layout_size: tuple[int, int] = (0, 0)
        self.rect = pygame.Rect(0, 0, 0, 0)
        self._label_font: pygame.font.Font
        self._value_font: pygame.font.Font
        self._fit_fonts: dict[int, pygame.font.Font] = {}
        self._panel_cache: dict[
            tuple[str, tuple[int, int]], pygame.Surface
        ] = {}
        font_path = (
            Path(__file__).resolve().parents[2]
            / "fonts" / "orbitron-semibold.ttf"
        )
        self._font_path = str(font_path) if font_path.is_file() else None
        self._update_layout()

    def _update_layout(self) -> None:
        """Recalculate the panel rectangle and fonts after a size change."""
        size = self.surface.get_size()
        if size == self._layout_size:
            return
        width, screen_height = size
        if width < 160 or screen_height <= self.height:
            raise ValueError("Game window is too small for the HUD.")
        padding = max(4, min(16, width // 50, self.height // 8))
        panel_width = min(width - padding * 2, round(width * 0.82))
        self.rect = pygame.Rect(
            (width - panel_width) // 2,
            padding,
            panel_width,
            self.height - padding * 2,
        )
        scale = min(width / 1200, self.height / 130)
        # Pygame's default face appears smaller than Orbitron at equal size.
        font_scale = scale * (1.35 if self._font_path is None else 1.0)
        self._label_font = pygame.font.Font(
            self._font_path, max(10, round(20 * font_scale)),
        )
        self._value_font = pygame.font.Font(
            self._font_path, max(13, round(32 * font_scale)),
        )
        self._fit_fonts.clear()
        self._layout_size = size

    def _panel_image(self, path: str) -> pygame.Surface:
        """Trim transparent image padding before fitting the visible panel."""
        key = (path, self.rect.size)
        if key not in self._panel_cache:
            source = self.asset_manager.load(path)
            bounds = source.get_bounding_rect(min_alpha=48)
            if bounds.width > 0 and bounds.height > 0:
                source = source.subsurface(bounds).copy()
            self._panel_cache[key] = pygame.transform.smoothscale(
                source, self.rect.size,
            )
        return self._panel_cache[key]

    def _draw_text(
        self,
        font: pygame.font.Font,
        text: str,
        center: tuple[int, int],
        color: tuple[int, int, int],
    ) -> None:
        """Center readable text over the panel with a small dark shadow."""
        shadow = font.render(text, True, (3, 5, 18))
        image = font.render(text, True, color)
        self.surface.blit(shadow, shadow.get_rect(center=(
            center[0] + 1, center[1] + 2,
        )))
        self.surface.blit(image, image.get_rect(center=center))

    def _draw_value(
        self,
        text: str,
        center: tuple[int, int],
        max_width: int,
        color: tuple[int, int, int],
    ) -> None:
        """Draw a value, reducing its font size if it exceeds its column."""
        font = self._value_font
        size = font.get_height()
        if font.size(text)[0] > max_width:
            size = max(8, round(size * max_width / font.size(text)[0]))
            if size not in self._fit_fonts:
                self._fit_fonts[size] = pygame.font.Font(self._font_path, size)
            font = self._fit_fonts[size]
        self._draw_text(font, text, center, color)

    def render(
        self,
        level: int,
        score: int,
        remaining_time: float,
        lives: int,
    ) -> None:
        """Draw current values with the selected theme's panel.

        Args:
            level: Current level number, displayed starting at one.
            score: Accumulated player score.
            remaining_time: Remaining seconds; rounded upward for display.
            lives: Remaining player lives.
        """
        self._update_layout()
        name = self.theme_manager.current.name
        path = self.PANEL_PATHS.get(name, self.PANEL_PATHS["ice"])
        panel = self._panel_image(path)
        self.surface.blit(panel, self.rect)
        seconds = (
            max(0, math.ceil(remaining_time))
            if math.isfinite(remaining_time) else 0
        )
        values = (
            str(max(1, level)),
            str(max(0, score)),
            f"{seconds // 60:02d}:{seconds % 60:02d}",
            str(max(0, lives)),
        )
        label_color = (195, 235, 255) if name == "ice" else (230, 200, 255)
        value_color = (255, 250, 225)
        column_width = self.rect.width // len(self.LABELS)
        for index, (label, value) in enumerate(zip(self.LABELS, values)):
            center_x = self.rect.left + round(
                self.rect.width * (index + 0.5) / len(self.LABELS),
            )
            self._draw_text(
                self._label_font,
                label,
                (center_x, self.rect.top + round(self.rect.height * 0.30)),
                label_color,
            )
            color = (
                (255, 100, 100)
                if label == "TIME" and seconds <= 10 else value_color
            )
            self._draw_value(
                value,
                (center_x, self.rect.top + round(self.rect.height * 0.66)),
                max(1, column_width - 16),
                color,
            )
