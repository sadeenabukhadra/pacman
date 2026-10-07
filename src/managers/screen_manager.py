"""Manage the active screen of the game."""

from src.screens.base_screen import BaseScreen


class ScreenManager:
    """Manage and switch between game screens."""

    def __init__(self) -> None:
        """Initialize the manager with no active screen."""
        self.current_screen: BaseScreen | None = None

    def change_screen(self, new_screen: BaseScreen) -> None:
        """Set a new screen as the active screen.

        Args:
            new_screen: The screen that should become active.
        """
        self.current_screen = new_screen
