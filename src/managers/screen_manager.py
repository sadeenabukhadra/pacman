"""Manage switching between game screens."""

from collections.abc import Callable
from typing import Any


class ScreenManager:
    """Hold the current screen and switch between registered screens."""

    def __init__(self) -> None:
        """Initialize the manager with no active screen."""
        self.current_screen: Any = None
        self._factories: dict[str, Callable[[], Any]] = {}

    def register(
        self,
        name: str,
        factory: Callable[[], Any],
    ) -> None:
        """Register a function that builds a screen by name."""
        self._factories[name] = factory

    def change_screen(self, screen: Any) -> None:
        """Switch to a screen given by name or as an object."""
        if isinstance(screen, str):
            factory = self._factories.get(screen)

            if factory is None:
                print(f"Screen '{screen}' is not registered yet.")
                return

            screen = factory()

        self.current_screen = screen

        # الشاشات المعاد استخدامها تصفّر حالتها عند كل دخول
        on_enter = getattr(screen, "on_enter", None)
        if callable(on_enter):
            on_enter()