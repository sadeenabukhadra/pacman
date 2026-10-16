from abc import ABC, abstractmethod

import pygame


class BaseScreen(ABC):
    def __init__(self, surface: pygame.Surface) -> None:
        """
        Initialize the screen with the surface used for drawing.

        Args:
            surface: The Pygame surface where the screen is rendered.
        """
        self.surface = surface

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None:
        """
        Handle a Pygame event received by the screen.

        Args:
            event: The Pygame event to process.
        """
        pass

    @abstractmethod
    def update(self, dt: float) -> None:
        """
        Update the state of the screen.

        Args:
            dt: Time elapsed since the previous frame, in seconds.
        """
        pass

    @abstractmethod
    def render(self) -> None:
        """
        Render the screen on its Pygame surface.
        """
        pass
