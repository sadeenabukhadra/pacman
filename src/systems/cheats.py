"""Keep optional peer-review cheats separate from normal game rules."""

from typing import Literal

import pygame


CheatAction = Literal["changed", "life", "next"]
CheatCommand = Literal[
    "mode", "invincible", "freeze_ghosts", "freeze_time",
    "fast", "life", "next",
]


class CheatMode:
    """Toggle review helpers; all helpers start disabled in a fresh game."""

    def __init__(self) -> None:
        """Start with ordinary gameplay and no persistent cheat settings."""
        self.enabled = False
        self.invincible = False
        self.freeze_ghosts = False
        self.freeze_time = False
        self.fast = False
        self._pressed: set[CheatCommand] = set()

    @staticmethod
    def _command(event: pygame.event.Event) -> CheatCommand | None:
        """Accept letter keys, physical key positions and F-key aliases."""
        bindings: tuple[tuple[int, int, CheatCommand], ...] = (
            (pygame.K_F1, pygame.KSCAN_F1, "mode"),
            (pygame.K_i, pygame.KSCAN_I, "invincible"),
            (pygame.K_f, pygame.KSCAN_F, "freeze_ghosts"),
            (pygame.K_t, pygame.KSCAN_T, "freeze_time"),
            (pygame.K_v, pygame.KSCAN_V, "fast"),
            (pygame.K_l, pygame.KSCAN_L, "life"),
            (pygame.K_n, pygame.KSCAN_N, "next"),
            (pygame.K_F2, pygame.KSCAN_F2, "invincible"),
            (pygame.K_F3, pygame.KSCAN_F3, "freeze_ghosts"),
            (pygame.K_F4, pygame.KSCAN_F4, "freeze_time"),
            (pygame.K_F5, pygame.KSCAN_F5, "fast"),
            (pygame.K_F6, pygame.KSCAN_F6, "life"),
            (pygame.K_F7, pygame.KSCAN_F7, "next"),
        )
        scan = getattr(event, "scancode", None)
        for key, scancode, command in bindings:
            if scan == scancode:
                return command
        for key, scancode, command in bindings:
            if getattr(event, "key", None) == key:
                return command
        return None

    @property
    def speed_multiplier(self) -> float:
        """Return a fixed multiplier so repeated toggles cannot stack."""
        return 2.0 if self.enabled and self.fast else 1.0

    def handle_event(self, event: pygame.event.Event) -> CheatAction | None:
        """Apply each shortcut once per press, accepting either layout."""
        if event.type == pygame.WINDOWFOCUSLOST:
            self._pressed.clear()
            return None
        if event.type == pygame.KEYUP:
            command = self._command(event)
            if command is not None:
                self._pressed.discard(command)
            return None
        if event.type != pygame.KEYDOWN:
            return None
        command = self._command(event)
        if command is None or (command != "mode" and not self.enabled):
            return None
        if command in self._pressed or getattr(event, "repeat", False):
            return "changed"
        self._pressed.add(command)
        if command == "mode":
            self.enabled = not self.enabled
            self.invincible = self.enabled
            self.freeze_ghosts = False
            self.freeze_time = False
            self.fast = False
        elif command == "life":
            return "life"
        elif command == "next":
            return "next"
        else:
            setattr(self, command, not getattr(self, command))
        return "changed"
