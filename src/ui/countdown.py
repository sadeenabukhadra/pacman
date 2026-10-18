"""Show a themed, non-blocking countdown before gameplay starts."""

import math

import pygame


class Countdown:
    """Display three one-second numbers followed by a short GO message."""

    COUNT_SECONDS = 3.0
    GO_SECONDS = 0.45

    def __init__(self, surface: pygame.Surface, area: pygame.Rect) -> None:
        """Keep the overlay inside the maze without covering the HUD."""
        self.surface = surface
        self.area = area.clip(surface.get_rect())
        self.elapsed = 0.0
        self._radius = max(1, min(66, min(self.area.size) // 6))
        self._number_font = pygame.font.Font(
            None, max(1, round(self._radius * 1.45)),
        )
        self._label_font = pygame.font.Font(
            None, max(12, self._radius // 4),
        )

    @property
    def active(self) -> bool:
        """Report whether both the numbers and GO still block gameplay."""
        return self.elapsed < self.COUNT_SECONDS + self.GO_SECONDS

    @property
    def message(self) -> str:
        """Return the visible number, GO, or an empty completed message."""
        if not self.active:
            return ""
        if self.elapsed >= self.COUNT_SECONDS:
            return "GO!"
        return str(math.ceil(self.COUNT_SECONDS - self.elapsed))

    def update(self, dt: float) -> None:
        """Advance only with finite positive frame time, never blocking."""
        if math.isfinite(dt) and dt > 0:
            self.elapsed = min(
                self.COUNT_SECONDS + self.GO_SECONDS,
                self.elapsed + dt,
            )

    def render(self, theme_name: str) -> None:
        """Draw a clear ice-blue or cosmic-purple circle over the maze."""
        if not self.active:
            return
        accent = (130, 230, 255) if theme_name == "ice" else (215, 150, 255)
        background = (6, 22, 40) if theme_name == "ice" else (22, 9, 43)
        overlay = pygame.Surface(self.area.size, pygame.SRCALPHA)
        overlay.fill((*background, 105))
        center = (self.area.width // 2, self.area.height // 2)
        radius = self._radius
        for extra, alpha in ((12, 25), (7, 50)):
            pygame.draw.circle(
                overlay, (*accent, alpha), center, radius + extra,
            )
        pygame.draw.circle(overlay, (*background, 242), center, radius)
        pygame.draw.circle(
            overlay, (*accent, 130), center, radius, width=2,
        )
        ring = pygame.Rect(0, 0, radius * 2 - 12, radius * 2 - 12)
        ring.center = center
        progress = 1.0 - (self.elapsed % 1.0)
        if self.elapsed >= self.COUNT_SECONDS:
            progress = 1.0
        pygame.draw.arc(
            overlay, accent, ring, math.pi / 2,
            math.pi / 2 + math.tau * progress, width=3,
        )
        label = self._label_font.render("GET READY", True, accent)
        overlay.blit(label, label.get_rect(center=(
            center[0], center[1] - radius // 2,
        )))
        number = self._number_font.render(self.message, True, (245, 250, 255))
        # Keep GO inside the same circle as the single-digit numbers.
        if number.get_width() > radius * 3 // 2:
            factor = (radius * 3 / 2) / number.get_width()
            number = pygame.transform.smoothscale(number, (
                max(1, round(number.get_width() * factor)),
                max(1, round(number.get_height() * factor)),
            ))
        overlay.blit(number, number.get_rect(center=(
            center[0], center[1] + radius // 6,
        )))
        self.surface.blit(overlay, self.area.topleft)
