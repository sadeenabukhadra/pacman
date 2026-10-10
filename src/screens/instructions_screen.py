"""Provide the instructions (how to play) screen."""

from collections.abc import Callable
from pathlib import Path

import pygame

from src.screens.base_screen import BaseScreen
from src.ui.button import Button

BACKGROUND_COLOR = (5, 8, 32)

# قياسات التصميم المرجعي للأزرار (نفس القائمة الرئيسية)
REF_W = 1536
REF_BUTTON_W, REF_BUTTON_H = 410, 74
REF_FONT_SIZE = 32

# موضع الزر داخل الصورة (نسبة من أبعاد الصورة)
BUTTON_CX = 0.50
BUTTON_CY = 0.915

# الزر أصغر قليلاً من أزرار القائمة ليناسب الصورة
BUTTON_SCALE_FACTOR = 0.8
IMAGE_DIR = Path("images/sitting")

class InstructionsScreen(BaseScreen):
    """Display the how-to-play image with a back button inside it."""

    def __init__(
        self,
        surface: pygame.Surface,
        change_screen: Callable[[str], None],
    ) -> None:
        """Initialize the instructions screen."""
        super().__init__(surface)
        self.change_screen = change_screen

        width, height = self.surface.get_size()
        scale = width / REF_W
        button_scale = scale * BUTTON_SCALE_FACTOR

        # الصورة بعرض النافذة وبنسبتها الأصلية، في منتصف النافذة عمودياً
        image = pygame.image.load(
            "images/instructions/how_to_play.png"
        ).convert()

        # 1) الصورة كاملة بعرض النافذة (بدون قص)
        image_height = round(width * image.get_height() / image.get_width())
        self.image = pygame.transform.smoothscale(image, (width, image_height))
        self.image_top = (height - image_height) // 2

        # 2) خلفية ممتدة: نفس الصورة مكبّرة لتغطي النافذة ثم مموّهة
        cover = max(width / image.get_width(), height / image.get_height())
        big = pygame.transform.smoothscale(
            image,
            (
                round(image.get_width() * cover),
                round(image.get_height() * cover),
            ),
        )
        crop = pygame.Rect(0, 0, width, height)
        crop.center = big.get_rect().center
        backdrop = big.subsurface(crop).copy()

        # تمويه بالتصغير ثم التكبير، وتغميق خفيف
        small = pygame.transform.smoothscale(
            backdrop, (width // 20, height // 20)
        )
        self.backdrop = pygame.transform.smoothscale(small, (width, height))
        dark = pygame.Surface((width, height))
        dark.set_alpha(110)
        self.backdrop.blit(dark, (0, 0))

        # الخط
        font_file = Path("fonts/orbitron-semibold.ttf")
        size = round(REF_FONT_SIZE * button_scale)
        font = (
            pygame.font.Font(str(font_file), size)
            if font_file.exists()
            else pygame.font.Font(None, round(size * 1.4))
        )

        # الزر داخل حدود الصورة
        rect = pygame.Rect(
            0,
            0,
            round(REF_BUTTON_W * button_scale),
            round(REF_BUTTON_H * button_scale),
        )
        rect.center = (
            round(width * BUTTON_CX),
            self.image_top + round(image_height * BUTTON_CY),
        )

        self.back_button = Button(
            rect=rect,
            text="BACK TO MENU",
            font=font,
            normal_image=pygame.image.load(
                str(IMAGE_DIR / "notselect_chose.png")
            ).convert_alpha(),
            selected_image=pygame.image.load(
                str(IMAGE_DIR / "selectchose.png")
            ).convert_alpha(),
            # صورة شفافة بدل النجمة
            star_image=pygame.Surface((1, 1), pygame.SRCALPHA),
        )
        self.back_button.set_selected(True)
        self.back_button.set_selected(True)

    def _go_back(self) -> None:
        """Return to the main menu."""
        self.change_screen("menu")

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle input."""
        if event.type == pygame.KEYDOWN:
            if event.key in (
                pygame.K_ESCAPE,
                pygame.K_RETURN,
                pygame.K_BACKSPACE,
            ):
                self._go_back()

        elif (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.back_button.is_hovered(event.pos)
        ):
            self._go_back()

    def update(self, dt: float) -> None:
        """Update the screen."""

    def render(self) -> None:
        """Draw the screen."""
        self.surface.blit(self.backdrop, (0, 0))
        self.surface.blit(self.image, (0, self.image_top))
        self.back_button.render(self.surface)