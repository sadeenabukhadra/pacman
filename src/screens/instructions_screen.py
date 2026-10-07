"""Provide the instructions screen of the game."""

from collections.abc import Callable

import pygame

from src.screens.base_screen import BaseScreen
from src.ui.button import Button


class InstructionsScreen(BaseScreen):
    """Display the game instructions to the player."""

    def __init__(
        self,
        surface: pygame.Surface,
        change_screen: Callable[[str], None],
    ) -> None:
        """Initialize the instructions screen.

        Args:
            surface: Surface where the screen is drawn.
            change_screen: Function used to request a screen change.
        """
        super().__init__(surface)

        self.change_screen = change_screen

        self.title_font = pygame.font.Font(None, 52)
        self.text_font = pygame.font.Font(None, 30)
        self.button_font = pygame.font.Font(None, 34)

        button_width = 250
        button_height = 55

        x = (
            self.surface.get_width() - button_width
        ) // 2

        y = self.surface.get_height() - 100

        self.back_button = Button(
            rect=pygame.Rect(
                x,
                y,
                button_width,
                button_height,
            ),
            text="BACK TO MENU",
            font=self.button_font,
            normal_color=(30, 45, 70),
            selected_color=(70, 160, 220),
        )

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle keyboard and mouse input."""
        if event.type == pygame.KEYDOWN:
            if event.key in (
                pygame.K_ESCAPE,
                pygame.K_RETURN,
            ):
                self.change_screen("menu")

        elif event.type == pygame.MOUSEMOTION:
            self.back_button.set_selected(
                self.back_button.is_hovered(event.pos)
            )

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if (
                event.button == 1
                and self.back_button.is_hovered(event.pos)
            ):
                self.change_screen("menu")

    def update(self, dt: float) -> None:
        """Update the instructions screen.

        Args:
            dt: Time elapsed since the previous frame.
        """
        pass

    def render(self) -> None:
        """Draw the instructions screen."""
        self.surface.fill((10, 20, 40))

        title = self.title_font.render(
            "PAC-MAN HOW TO PLAY",
            True,
            (255, 255, 255),
        )

        title_rect = title.get_rect(
            center=(
                self.surface.get_width() // 2,
                70,
            )
        )

        self.surface.blit(title, title_rect)

        instructions = [
            "MOVE: Use Arrow Keys or WASD",
            "GOAL: Collect all small dots",
            "POWER: Crystals make ghosts edible",
            "DANGER: Avoid ghosts when normal",
            "LIVES: You start with 3 lives",
            "LEVEL: Clear all dots to advance",
            "PAUSE: Press P or ESC",
        ]

        start_y = 150

        for index, instruction in enumerate(instructions):
            text = self.text_font.render(
                instruction,
                True,
                (220, 230, 240),
            )

            text_rect = text.get_rect(
                center=(
                    self.surface.get_width() // 2,
                    start_y + index * 55,
                )
            )

            self.surface.blit(text, text_rect)

        self.back_button.render(self.surface)
