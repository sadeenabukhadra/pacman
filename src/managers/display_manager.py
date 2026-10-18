"""Own native display changes while keeping menu coordinates stable."""

import pygame

from src.systems.display_layout import DisplayPlan, plan_display


class DisplayManager:
    """Use real desktop pixels for gameplay and a fixed menu canvas."""

    def __init__(self, fullscreen: bool = False) -> None:
        """Detect the primary desktop and open a bounded initial display."""
        desktops = pygame.display.get_desktop_sizes()
        if not desktops or min(desktops[0]) < 1:
            raise RuntimeError("Cannot determine the desktop size.")
        self.desktop = desktops[0]
        self.fullscreen = fullscreen
        self.base_size = (1200, 800)
        self.surface = self._set(self.menu_size(), fullscreen)

    def menu_size(self) -> tuple[int, int]:
        """Fit the menu window, retaining native resolution in fullscreen."""
        if self.fullscreen:
            return self.desktop
        return (
            min(self.base_size[0], max(1, self.desktop[0] - 32)),
            min(self.base_size[1], max(1, self.desktop[1] - 80)),
        )

    def _set(
        self, size: tuple[int, int], fullscreen: bool,
    ) -> pygame.Surface:
        """Resize without SCALED so display pixels match gameplay pixels."""
        flags = pygame.FULLSCREEN if fullscreen else 0
        surface = pygame.display.set_mode(size, flags)
        if not fullscreen:
            try:
                pygame.display.set_window_position((
                    max(0, (self.desktop[0] - size[0]) // 2),
                    max(32, (self.desktop[1] - size[1]) // 2),
                ))
            except pygame.error:
                pass  # Some window managers place windows themselves.
        return surface

    def show_menu(self) -> None:
        """Return windowed menus to their ordinary bounded dimensions."""
        if self.surface.get_size() != self.menu_size():
            self.surface = self._set(self.menu_size(), self.fullscreen)

    def set_fullscreen(self, enabled: bool) -> None:
        """Change native mode, retaining the old mode if SDL rejects it."""
        if enabled == self.fullscreen:
            return
        old_size, old_mode = self.surface.get_size(), self.fullscreen
        self.fullscreen = enabled
        try:
            self.surface = self._set(self.menu_size(), enabled)
        except pygame.error:
            self.fullscreen = old_mode
            self.surface = self._set(old_size, old_mode)
            raise

    def prepare_maze(
        self, size: tuple[int, int], preferred_tile: int, hud_height: int,
        margin: int,
    ) -> DisplayPlan:
        """Apply a screen-safe layout before building the next level view."""
        plan = plan_display(
            size, preferred_tile, self.desktop, self.fullscreen,
            hud_height, margin, self.base_size,
        )
        if self.surface.get_size() != plan.size:
            self.surface = self._set(plan.size, self.fullscreen)
        return plan

    def restore_size(self, size: tuple[int, int]) -> None:
        """Restore a previous window size after a level preparation failure."""
        if self.surface.get_size() != size:
            self.surface = self._set(size, self.fullscreen)

    def canvas_rect(self, size: tuple[int, int]) -> pygame.Rect:
        """Center a logical menu canvas without distorting its proportions."""
        width, height = self.surface.get_size()
        factor = min(width / size[0], height / size[1])
        rect = pygame.Rect(
            0, 0, max(1, round(size[0] * factor)),
            max(1, round(size[1] * factor)),
        )
        rect.center = self.surface.get_rect().center
        return rect

    def present_canvas(self, canvas: pygame.Surface) -> None:
        """Draw existing menus with letterboxing on the native display."""
        rect = self.canvas_rect(canvas.get_size())
        self.surface.fill((0, 0, 0))
        self.surface.blit(
            pygame.transform.smoothscale(canvas, rect.size), rect,
        )

    def canvas_event(
        self, event: pygame.event.Event, size: tuple[int, int],
    ) -> pygame.event.Event | None:
        """Map mouse positions and motion into the logical menu canvas."""
        if not hasattr(event, "pos"):
            return event
        rect = self.canvas_rect(size)
        if not rect.collidepoint(event.pos):
            return None
        attributes = event.dict.copy()
        attributes["pos"] = (
            int((event.pos[0] - rect.left) * size[0] / rect.width),
            int((event.pos[1] - rect.top) * size[1] / rect.height),
        )
        if "rel" in attributes:
            attributes["rel"] = (
                round(event.rel[0] * size[0] / rect.width),
                round(event.rel[1] * size[1] / rect.height),
            )
        return pygame.event.Event(event.type, attributes)
