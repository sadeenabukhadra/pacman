from src.screens.base_screen import BaseScreen


class ScreenManager:
    def __init__(self) -> None:
        """Initialize the screen manager with no active screen."""
        self.current_screen: BaseScreen | None = None

    def change_screen(self, new_screen: BaseScreen) -> None:
        """Change the currently active screen.

        Args:
            new_screen: The screen that should become active.
        """
        self.current_screen = new_screen
