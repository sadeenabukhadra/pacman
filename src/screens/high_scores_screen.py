"""Provide the high scores screen."""

from collections.abc import Callable
from pathlib import Path

import pygame

from src.managers.score_manager import MAX_SCORES, load_scores
from src.screens.base_screen import BaseScreen
from src.ui.button import Button

IMAGE_DIR = Path("images/highscore")
SETTINGS_IMAGE_DIR = Path("images/sitting")   # صور زر BACK (نفس ستايل Settings)

# قياسات الصورة الأصلية (1672 x 941) -- كل المواضع أدناه بإحداثياتها
REF_IMG_W = 1672

# الجدول: 10 صفوف متساوية تحت صف العناوين
REF_HEADER_Y = 297
REF_FIRST_ROW_Y = 346
REF_ROW_STEP = 48.8
REF_TABLE_CENTER_X = 836
REF_TABLE_CENTER_Y = 550

REF_RANK_X = 450      # عمود الترتيب (توسيط)
REF_NAME_X = 560      # عمود الاسم (محاذاة يسار)
REF_SCORE_X = 1250    # عمود النتيجة (محاذاة يمين)

REF_BACK_CY = 895     # مركز زر الرجوع

# شرائط الصفوف
ROW_BAR_W = 1010      # عرض الشريط بإحداثيات الصورة الأصلية
BAR_MIN_ALPHA = 90    # شفافية أقل من هذا تُقص من هامش الصورة

# قياسات بكسلات النافذة (1200 x 800) وتتكيف مع العرض
WINDOW_REF_W = 1200
ROW_FONT_SIZE = 22
HEADER_FONT_SIZE = 20
EMPTY_FONT_SIZE = 28
EMPTY_SUB_FONT_SIZE = 17
BUTTON_W, BUTTON_H = 300, 58
BUTTON_FONT_SIZE = 22

HEADER_COLOR = (120, 230, 255)
TEXT_COLOR = (235, 245, 255)
EMPTY_COLOR = (170, 215, 255)
RANK_COLORS = {
    0: (255, 235, 150),   # الأول: ذهبي فاتح فوق الشريط الذهبي
}


def _load_font(path: str, size: int) -> pygame.font.Font:
    """Load a TTF font, or fall back to the default font."""
    font_file = Path(path)
    if font_file.exists():
        return pygame.font.Font(str(font_file), size)
    return pygame.font.Font(None, round(size * 1.4))


def _load_bar(path: Path, width: int) -> pygame.Surface:
    """Load a row bar, trim its transparent margin and set its width."""
    image = pygame.image.load(str(path)).convert_alpha()
    image = image.subsurface(
        image.get_bounding_rect(min_alpha=BAR_MIN_ALPHA)
    ).copy()
    height = round(image.get_height() * width / image.get_width())
    return pygame.transform.smoothscale(image, (width, height))


class HighScoresScreen(BaseScreen):
    """Display the best scores in a table with a back button."""

    def __init__(
        self,
        surface: pygame.Surface,
        change_screen: Callable[[str], None],
    ) -> None:
        """Initialize the high scores screen."""
        super().__init__(surface)
        self.change_screen = change_screen

        width, height = self.surface.get_size()
        win_scale = width / WINDOW_REF_W

        # -------------------------
        # Background: كامل الصورة + خلفية ممتدة ومموهة خلفها
        # -------------------------

        image = pygame.image.load(
            str(IMAGE_DIR / "wallpaper_highscore.png")
        ).convert()

        image_height = round(width * image.get_height() / image.get_width())
        self.image = pygame.transform.smoothscale(image, (width, image_height))
        self.image_top = (height - image_height) // 2
        self.s = width / REF_IMG_W   # معامل تحويل إحداثيات الصورة

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

        small = pygame.transform.smoothscale(
            backdrop,
            (max(1, width // 20), max(1, height // 20)),
        )
        self.backdrop = pygame.transform.smoothscale(small, (width, height))
        dark = pygame.Surface((width, height))
        dark.set_alpha(110)
        self.backdrop.blit(dark, (0, 0))

        # -------------------------
        # Fonts
        # -------------------------

        font_path = "fonts/orbitron-semibold.ttf"
        self.row_font = _load_font(font_path, round(ROW_FONT_SIZE * win_scale))
        self.header_font = _load_font(
            font_path,
            round(HEADER_FONT_SIZE * win_scale),
        )
        self.empty_font = _load_font(
            font_path,
            round(EMPTY_FONT_SIZE * win_scale),
        )
        self.empty_sub_font = _load_font(
            "fonts/orbitron-regular.ttf",
            round(EMPTY_SUB_FONT_SIZE * win_scale),
        )
        button_font = _load_font(
            font_path,
            round(BUTTON_FONT_SIZE * win_scale),
        )

        # -------------------------
        # Row bars (الأول ذهبي، الباقي أزرق)
        # -------------------------

        bar_width = self._x(ROW_BAR_W)
        self.first_bar = _load_bar(
            IMAGE_DIR / "first_user_inscore.png",
            bar_width,
        )
        self.other_bar = _load_bar(
            IMAGE_DIR / "scound_users_inscore.png",
            bar_width,
        )

        # -------------------------
        # Back button (نفس ستايل Settings، بدون نجمة)
        # -------------------------

        rect = pygame.Rect(
            0,
            0,
            round(BUTTON_W * win_scale),
            round(BUTTON_H * win_scale),
        )
        rect.center = (width // 2, self._y(REF_BACK_CY))

        self.back_button = Button(
            rect=rect,
            text="BACK TO MENU",
            font=button_font,
            normal_image=pygame.image.load(
                str(SETTINGS_IMAGE_DIR / "notselect_chose.png")
            ).convert_alpha(),
            selected_image=pygame.image.load(
                str(SETTINGS_IMAGE_DIR / "selectchose.png")
            ).convert_alpha(),
            star_image=pygame.Surface((1, 1), pygame.SRCALPHA),
        )
        self.back_button.set_selected(True)

        self.scores: list[dict] = []
        self.on_enter()

    # -------------------------
    # Helpers
    # -------------------------

    def _x(self, ref_x: float) -> int:
        """Convert an image x position to a window x position."""
        return round(ref_x * self.s)

    def _y(self, ref_y: float) -> int:
        """Convert an image y position to a window y position."""
        return self.image_top + round(ref_y * self.s)

    def on_enter(self) -> None:
        """Reload the scores from disk (dynamic data)."""
        self.scores = load_scores()[:MAX_SCORES]

    def _go_back(self) -> None:
        """Return to the main menu."""
        self.change_screen("menu")

    # -------------------------
    # Events
    # -------------------------

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

    # -------------------------
    # Drawing
    # -------------------------

    def _draw_text(
        self,
        font: pygame.font.Font,
        text: str,
        color: tuple[int, int, int],
        position: tuple[int, int],
        anchor: str,
    ) -> None:
        """Draw text anchored on a window position."""
        text_surface = font.render(text, True, color)
        rect = text_surface.get_rect(**{anchor: position})
        self.surface.blit(text_surface, rect)

    def _draw_headers(self) -> None:
        """Draw the table column titles."""
        y = self._y(REF_HEADER_Y)
        self._draw_text(
            self.header_font, "RANK", HEADER_COLOR,
            (self._x(REF_RANK_X), y), "center",
        )
        self._draw_text(
            self.header_font, "NAME", HEADER_COLOR,
            (self._x(REF_NAME_X), y), "midleft",
        )
        self._draw_text(
            self.header_font, "SCORE", HEADER_COLOR,
            (self._x(REF_SCORE_X), y), "midright",
        )

    def _draw_rows(self) -> None:
        """Draw one row (with its bar) per saved score."""
        for index, entry in enumerate(self.scores):
            y = self._y(REF_FIRST_ROW_Y + index * REF_ROW_STEP)
            color = RANK_COLORS.get(index, TEXT_COLOR)

            bar = self.first_bar if index == 0 else self.other_bar
            self.surface.blit(
                bar,
                bar.get_rect(center=(self._x(REF_TABLE_CENTER_X), y)),
            )

            self._draw_text(
                self.row_font, str(index + 1), color,
                (self._x(REF_RANK_X), y), "center",
            )
            self._draw_text(
                self.row_font, entry["name"].upper(), color,
                (self._x(REF_NAME_X), y), "midleft",
            )
            self._draw_text(
                self.row_font, f"{entry['score']:,}", color,
                (self._x(REF_SCORE_X), y), "midright",
            )

    def _draw_empty_message(self) -> None:
        """Draw the message shown when no user has a score yet."""
        center_x = self._x(REF_TABLE_CENTER_X)
        center_y = self._y(REF_TABLE_CENTER_Y)

        self._draw_text(
            self.empty_font, "NO USERS YET", EMPTY_COLOR,
            (center_x, center_y - 14), "center",
        )
        self._draw_text(
            self.empty_sub_font, "PLAY A GAME TO APPEAR HERE", HEADER_COLOR,
            (center_x, center_y + 24), "center",
        )

    def render(self) -> None:
        """Draw the screen."""
        self.surface.blit(self.backdrop, (0, 0))
        self.surface.blit(self.image, (0, self.image_top))

        self._draw_headers()

        if self.scores:
            self._draw_rows()
        else:
            self._draw_empty_message()

        self.back_button.render(self.surface)