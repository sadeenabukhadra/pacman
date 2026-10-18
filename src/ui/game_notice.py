"""Draw readable gameplay notices using the active theme's palette."""

import pygame


class GameNotice:
    """Show a compact themed panel inside the maze, below the HUD."""

    def __init__(self, surface: pygame.Surface, area: pygame.Rect) -> None:
        """Cache fonts and a maze-sized translucent backdrop."""
        self.surface = surface
        self.area = area.clip(surface.get_rect())
        width = max(1, min(480, round(self.area.width * 0.84)))
        height = max(1, min(228, round(self.area.height * 0.42)))
        self.panel = pygame.Rect(0, 0, width, height)
        self.panel.center = (self.area.width // 2, self.area.height // 2)
        self._title_font = pygame.font.Font(None, max(12, height // 4))
        self._detail_font = pygame.font.Font(None, max(12, height // 7))
        self._label_font = pygame.font.Font(None, max(10, height // 10))
        self._overlay = pygame.Surface(self.area.size, pygame.SRCALPHA)

    def _text(
        self,
        text: str,
        font: pygame.font.Font,
        color: tuple[int, int, int],
        y_fraction: float,
    ) -> None:
        """Center text and shrink it only when panel width requires it."""
        image = font.render(text, True, color)
        available = max(1, round(self.panel.width * 0.84))
        if image.get_width() > available:
            factor = available / image.get_width()
            image = pygame.transform.smoothscale(image, (
                available, max(1, round(image.get_height() * factor)),
            ))
        rect = image.get_rect(center=(
            self.panel.centerx,
            self.panel.top + round(self.panel.height * y_fraction),
        ))
        self._overlay.blit(image, rect)

    def render(
        self,
        theme_name: str,
        title: str,
        detail: str,
        progress: float | None = None,
        footer: str = "",
        secondary: str = "",
        caption: str | None = None,
    ) -> None:
        """Draw ice-blue or cosmic-purple trim and an optional resume bar."""
        ice = theme_name == "ice"
        accent = (130, 230, 255) if ice else (215, 150, 255)
        muted = (175, 208, 228) if ice else (206, 184, 230)
        background = (6, 22, 40) if ice else (22, 9, 43)
        overlay = self._overlay
        overlay.fill((*background, 115))
        rect = self.panel
        cut = max(1, min(22, rect.height // 8, rect.width // 8))
        points = (
            (rect.left + cut, rect.top),
            (rect.right - cut, rect.top),
            (rect.right, rect.top + cut),
            (rect.right, rect.bottom - cut),
            (rect.right - cut, rect.bottom),
            (rect.left + cut, rect.bottom),
            (rect.left, rect.bottom - cut),
            (rect.left, rect.top + cut),
        )
        pygame.draw.polygon(overlay, (*background, 248), points)
        pygame.draw.polygon(overlay, (*accent, 45), points, width=9)
        pygame.draw.polygon(overlay, accent, points, width=2)
        label = caption or (
            "-1 LIFE" if progress is not None else "RUN COMPLETE"
        )
        self._text(label, self._label_font, accent, 0.19)
        self._text(title, self._title_font, (245, 250, 255), 0.43)
        self._text(
            detail, self._detail_font, accent, 0.59 if secondary else 0.65,
        )
        if secondary:
            self._text(secondary, self._label_font, muted, 0.73)
        if footer:
            self._text(
                footer, self._label_font, muted, 0.86 if secondary else 0.82,
            )
        if progress is not None:
            self._text("GET READY TO CONTINUE", self._label_font, muted, 0.80)
            bar = pygame.Rect(
                rect.left + round(rect.width * 0.18),
                rect.top + round(rect.height * 0.91),
                max(1, round(rect.width * 0.64)),
                max(2, round(rect.height * 0.018)),
            )
            pygame.draw.rect(overlay, (*accent, 45), bar, border_radius=3)
            filled = bar.copy()
            filled.width = round(bar.width * max(0.0, min(1.0, progress)))
            if filled.width > 0:
                pygame.draw.rect(overlay, accent, filled, border_radius=3)
        self.surface.blit(overlay, self.area.topleft)
