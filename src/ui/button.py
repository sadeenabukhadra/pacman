import pygame


class Button:
    """A reusable button for the game's user interface."""

    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        font: pygame.font.Font,
        normal_color: tuple[int, int, int],
        selected_color: tuple[int, int, int],
        text_color: tuple[int, int, int] = (255, 255, 255),
    ) -> None:
        """Initialize a button.

        Args:
            rect: Position and size of the button.
            text: Text displayed inside the button.
            font: Font used to render the text.
            normal_color: Button color in its normal state.
            selected_color: Button color when selected or hovered.
            text_color: Color of the button text.
        """
        self.rect: pygame.Rect = rect
        self.text: str = text
        self.font: pygame.font.Font = font

        self.normal_color: tuple[int, int, int] = normal_color
        self.selected_color: tuple[int, int, int] = selected_color
        self.text_color: tuple[int, int, int] = text_color

        self.selected: bool = False

    def is_hovered(self, position: tuple[int, int]) -> bool:
        """Return True if a position is inside the button."""
        return self.rect.collidepoint(position)

    def set_selected(self, selected: bool) -> None:
        """Set the selected state of the button."""
        self.selected = selected

    def render(self, surface: pygame.Surface) -> None:
        """Draw the button on the given surface."""
        color = self.selected_color if self.selected else self.normal_color

        pygame.draw.rect(
            surface,
            color,
            self.rect,
            border_radius=8,
        )

        text_surface = self.font.render(
            self.text,
            True,
            self.text_color,
        )

        text_rect = text_surface.get_rect(center=self.rect.center)

        surface.blit(text_surface, text_rect)
