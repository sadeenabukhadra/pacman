"""Display active review shortcuts without changing game state."""

import pygame

from src.systems.cheats import CheatMode


class CheatPanel:
    """Draw a themed shortcut panel, using the left margin when possible."""

    def __init__(self, surface: pygame.Surface) -> None:
        """Cache the fonts used by the review controls."""
        self.surface = surface
        self._title_font = pygame.font.Font(None, 24)
        self._font = pygame.font.Font(None, 21)

    def render(
        self, cheats: CheatMode, maze_area: pygame.Rect, theme_name: str,
    ) -> None:
        """Show every toggle's current state only while cheats are enabled."""
        if not cheats.enabled:
            return
        accent = (130, 230, 255) if theme_name == "ice" else (215, 150, 255)
        left_space = maze_area.left - 24
        width = min(250, left_space) if left_space >= 220 else 250
        width = max(1, min(width, self.surface.get_width() - 24))
        x = 12 if left_space >= 220 else maze_area.left + 12
        x = max(0, min(x, self.surface.get_width() - width))
        height = min(224, self.surface.get_height())
        y = max(0, min(maze_area.top + 18,
                       self.surface.get_height() - height))
        panel = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(
            panel, (6, 12, 30, 235), panel.get_rect(), border_radius=12,
        )
        pygame.draw.rect(
            panel, accent, panel.get_rect(), width=2, border_radius=12,
        )
        rows = (
            "CHEAT MODE  [F1]",
            f"I / F2   Shield: {'ON' if cheats.invincible else 'OFF'}",
            f"F / F3   Ghosts: {'FROZEN' if cheats.freeze_ghosts else 'MOVE'}",
            f"T / F4   Timer: {'FROZEN' if cheats.freeze_time else 'RUN'}",
            f"V / F5   Speed: {'2x' if cheats.fast else '1x'}",
            "L / F6   Add one life",
            "N / F7   Next level / win",
        )
        for index, row in enumerate(rows):
            font = self._title_font if index == 0 else self._font
            color = accent if index == 0 else (235, 240, 255)
            text = font.render(row, True, color)
            if text.get_width() > width - 24:
                available = max(1, width - 24)
                factor = available / text.get_width()
                text = pygame.transform.smoothscale(text, (
                    available, max(1, round(text.get_height() * factor)),
                ))
            panel.blit(text, (12, 14 + index * 28))
        self.surface.blit(panel, (x, y))
