"""Manage creation and switching of game screens."""

from collections.abc import Callable

from src.screens.base_screen import BaseScreen


ScreenFactory = Callable[[], BaseScreen]


class ScreenManager:
    """Manage registered game screens and the active screen."""

    def __init__(self) -> None:
        """Initialize the screen manager."""
        self.current_screen: BaseScreen | None = None
        self._screens: dict[str, ScreenFactory] = {}

    def register(
        self,
        name: str,
        factory: ScreenFactory,
    ) -> None:
        """Register a screen.

        Args:
            name: Unique screen name.
            factory: Function that creates the screen.
        """
        self._screens[name] = factory

    def change_screen(self, name: str) -> None:
        """Change the active screen.

        Args:
            name: Name of the registered screen.

        Raises:
            ValueError: If the screen is not registered.
        """
        if name not in self._screens:
            raise ValueError(
                f"Screen '{name}' is not registered."
            )

        self.current_screen = self._screens[name]()

        on_enter = getattr(
            self.current_screen,
            "on_enter",
            None,
        )

        if callable(on_enter):
            on_enter()

    def has_screen(self, name: str) -> bool:
        """Check whether a screen is registered.

        Args:
            name: Screen name.

        Returns:
            True if the screen exists.
        """
        return name in self._screens