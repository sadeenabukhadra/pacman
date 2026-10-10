"""Provide an image-based menu button."""

import pygame

# أي بكسل شفافيته أقل من هذه القيمة يُعتبر توهجاً وليس جسم الزر.
# إن ظهر الزر المحدد أكبر أو أصغر من العادي، غيّر هذه القيمة (100 - 220).
CORE_ALPHA = 150


def _fit_by_core(
    image: pygame.Surface,
    core_size: tuple[int, int],
) -> tuple[pygame.Surface, tuple[int, int]]:
    """Scale image so its opaque core matches core_size.

    Return the scaled image and the offset from the core center
    to the image top-left corner.
    """
    core = image.get_bounding_rect(min_alpha=CORE_ALPHA)

    scale_x = core_size[0] / core.width
    scale_y = core_size[1] / core.height

    scaled = pygame.transform.smoothscale(
        image,
        (
            round(image.get_width() * scale_x),
            round(image.get_height() * scale_y),
        ),
    )

    offset = (
        -round(core.centerx * scale_x),
        -round(core.centery * scale_y),
    )
    return scaled, offset


class Button:
    """Represent a selectable menu button."""

    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        font: pygame.font.Font,
        normal_image: pygame.Surface,
        selected_image: pygame.Surface,
        star_image: pygame.Surface,
    ) -> None:
        """Initialize the button."""
        self.rect = rect
        self.text = text
        self.font = font
        self.selected = False

        self.normal_image, self.normal_offset = _fit_by_core(
            normal_image,
            rect.size,
        )
        self.selected_image, self.selected_offset = _fit_by_core(
            selected_image,
            rect.size,
        )

        # النجمة: نحافظ على النسبة، وارتفاعها أكبر قليلاً من الزر
        star_height = round(rect.height * 1.2)
        star_width = round(
            star_image.get_width()
            * star_height
            / star_image.get_height()
        )
        self.star_image = pygame.transform.smoothscale(
            star_image,
            (star_width, star_height),
        )

        # النص يُرسم مرة واحدة بدل كل إطار
        self.text_surface = font.render(text, True, (245, 245, 255))

    def set_selected(self, selected: bool) -> None:
        """Set the selected state."""
        self.selected = selected

    def is_hovered(self, position: tuple[int, int]) -> bool:
        """Check whether mouse is over button."""
        return self.rect.collidepoint(position)

    def render(self, surface: pygame.Surface) -> None:
        """Draw the button."""
        if self.selected:
            image, offset = self.selected_image, self.selected_offset
        else:
            image, offset = self.normal_image, self.normal_offset

        surface.blit(
            image,
            (
                self.rect.centerx + offset[0],
                self.rect.centery + offset[1],
            ),
        )

        surface.blit(
            self.text_surface,
            self.text_surface.get_rect(center=self.rect.center),
        )

        if self.selected:
            star_rect = self.star_image.get_rect(
                center=(self.rect.left - 4, self.rect.centery),
            )
            surface.blit(self.star_image, star_rect)