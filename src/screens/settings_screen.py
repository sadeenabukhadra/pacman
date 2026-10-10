"""Provide the settings screen."""

from collections.abc import Callable
from pathlib import Path

import pygame

from src.managers.settings_manager import load_settings, save_settings
from src.screens.base_screen import BaseScreen
from src.ui.button import Button

IMAGE_DIR = Path("images/sitting")
# كل القياسات أدناه لنافذة 1200 x 800 وتتكيف مع المعامل scale
REF_W = 1200

# الخلفية 16:9 داخل نافذة 3:2: تُقص من الجانبين، وهذا يحدد أي جزء يبقى
BG_ANCHOR = 0.515

# لوحتا العالمين
PANEL_W = 540
PANEL_CY = 385
PANEL_CX = (320, 880)

# أشرطة الإعدادات
BAR_W = 370
BAR_CY = 590
BAR_CX = (210, 600, 990)

# موضع المفتاح داخل الشريط: (مركز أفقي، عرض) كنسبة من عرض الشريط
MUSIC_SLOT = (0.7435, 0.331)
SOUND_SLOT = (0.789, 0.252)
SCREEN_SLOT = (0.74, 0.37)
SCREEN_SLOT_H = 0.42   # ارتفاع القائمة كنسبة من ارتفاع الشريط

# الأزرار السفلية
BTN_W, BTN_H = 300, 62
BTN_CY = 705
BTN_CX = (430, 770)
BTN_FONT = 22
MESSAGE_CY = 765

TRIM_ALPHA = 90   # شفافية أقل من هذا تُعتبر توهجاً وتُقص

FOCUS_COLOR = (255, 90, 220)
DROPDOWN_FILL = (6, 14, 50)
DROPDOWN_BORDER = (70, 170, 255)
TEXT_COLOR = (235, 250, 255)
MESSAGE_COLOR = (170, 245, 255)

# ترتيب التنقل بالأسهم
GRID = [
    ["ice", "cosmic"],
    ["music", "sound", "screen"],
    ["save", "back"],
]
POSITIONS = {
    name: (row, col)
    for row, names in enumerate(GRID)
    for col, name in enumerate(names)
}


def _load_font(path: str, size: int) -> pygame.font.Font:
    """Load a TTF font, or fall back to the default font."""
    font_file = Path(path)
    if font_file.exists():
        return pygame.font.Font(str(font_file), size)
    return pygame.font.Font(None, round(size * 1.4))


def _load_image(name: str, width: int | None = None) -> pygame.Surface:
    """Load an image, trim its transparent margin, optionally set width."""
    image = pygame.image.load(str(IMAGE_DIR / name)).convert_alpha()
    image = image.subsurface(
        image.get_bounding_rect(min_alpha=TRIM_ALPHA)
    ).copy()

    if width is not None:
        height = round(image.get_height() * width / image.get_width())
        image = pygame.transform.smoothscale(image, (width, height))

    return image


class SettingsScreen(BaseScreen):
    """Let the player choose the world, sound and screen mode."""

    def __init__(
        self,
        surface: pygame.Surface,
        change_screen: Callable[[str], None],
    ) -> None:
        """Initialize the settings screen."""
        super().__init__(surface)
        self.change_screen = change_screen

        width, height = self.surface.get_size()
        self.scale = width / REF_W
        scale = self.scale

        def px(value: float) -> int:
            return round(value * scale)

        self.settings = load_settings()
        self.focus = POSITIONS[self.settings["world"]]
        self.message_time = 0.0

        # -------------------------
        # Background (cover + crop)
        # -------------------------

        wallpaper = pygame.image.load(
            str(IMAGE_DIR / "wellpaper.png")
        ).convert()
        cover = max(
            width / wallpaper.get_width(),
            height / wallpaper.get_height(),
        )
        wallpaper = pygame.transform.smoothscale(
            wallpaper,
            (
                round(wallpaper.get_width() * cover),
                round(wallpaper.get_height() * cover),
            ),
        )
        left = round(wallpaper.get_width() * BG_ANCHOR - width / 2)
        left = max(0, min(left, wallpaper.get_width() - width))
        top = max(0, (wallpaper.get_height() - height) // 2)
        self.background = wallpaper.subsurface(
            pygame.Rect(left, top, width, height)
        ).copy()

        # -------------------------
        # World panels
        # -------------------------

        self.world_images: dict[tuple[str, bool], pygame.Surface] = {}
        self.rects: dict[str, pygame.Rect] = {}

        for name, center_x in zip(("ice", "cosmic"), PANEL_CX):
            for selected, suffix in ((True, "check"), (False, "notcheck")):
                self.world_images[(name, selected)] = _load_image(
                    f"{name}_theme_{suffix}.png",
                    px(PANEL_W),
                )

            rect = self.world_images[(name, False)].get_rect()
            rect.center = (px(center_x), px(PANEL_CY))
            self.rects[name] = rect

        # -------------------------
        # Setting bars
        # -------------------------

        bar_files = {
            "music": "muisc_without_toogglo.png",
            "sound": "soundeffect_without_toggle.png",
            "screen": "chosse_screenmod_without_any_chose.png",
        }
        self.bar_images: dict[str, pygame.Surface] = {}

        for (name, file_name), center_x in zip(bar_files.items(), BAR_CX):
            image = _load_image(file_name, px(BAR_W))
            rect = image.get_rect()
            rect.center = (px(center_x), px(BAR_CY))
            self.bar_images[name] = image
            self.rects[name] = rect

        # -------------------------
        # Toggles
        # -------------------------

        self.slots = {
            "music": MUSIC_SLOT,
            "sound": SOUND_SLOT,
            "screen": SCREEN_SLOT,
        }
        self.toggle_images: dict[tuple[str, bool], pygame.Surface] = {}

        for name in ("music", "sound"):
            toggle_width = round(self.slots[name][1] * self.rects[name].width)
            for state, file_name in ((True, "toggle_on.png"), (False, "toggle_off.png")):
                self.toggle_images[(name, state)] = _load_image(
                    file_name,
                    toggle_width,
                )

        self.dropdown_font = _load_font(
            "fonts/orbitron-semibold.ttf",
            px(14),
        )

        # -------------------------
        # Bottom buttons
        # -------------------------

        button_font = _load_font(
            "fonts/orbitron-semibold.ttf",
            px(BTN_FONT),
        )
        normal = pygame.image.load(
            str(IMAGE_DIR / "notselect_chose.png")
        ).convert_alpha()
        selected = pygame.image.load(
            str(IMAGE_DIR / "selectchose.png")
        ).convert_alpha()
        star = pygame.Surface((1, 1), pygame.SRCALPHA)

        self.buttons: dict[str, Button] = {}

        for name, text, center_x in zip(
            ("save", "back"),
            ("SAVE SETTINGS", "BACK TO MENU"),
            BTN_CX,
        ):
            rect = pygame.Rect(0, 0, px(BTN_W), px(BTN_H))
            rect.center = (px(center_x), px(BTN_CY))
            self.rects[name] = rect
            self.buttons[name] = Button(
                rect=rect,
                text=text,
                font=button_font,
                normal_image=normal,
                selected_image=selected,
                star_image=star,
            )

        self.message_surface = button_font.render(
            "SETTINGS SAVED",
            True,
            MESSAGE_COLOR,
        )
        self.message_center = (width // 2, px(MESSAGE_CY))

    # -------------------------
    # Logic
    # -------------------------

    @property
    def focus_name(self) -> str:
        """Return the name of the focused item."""
        row, col = self.focus
        return GRID[row][col]

    def _move(self, d_row: int, d_col: int) -> None:
        """Move the focus inside the grid."""
        row, col = self.focus

        if d_row:
            row = (row + d_row) % len(GRID)
            col = min(col, len(GRID[row]) - 1)
        else:
            col = max(0, min(col + d_col, len(GRID[row]) - 1))

        self.focus = (row, col)

    def _activate(self, name: str) -> None:
        """Apply the action of an item."""
        if name in ("ice", "cosmic"):
            self.settings["world"] = name
        elif name == "music":
            self.settings["music"] = not self.settings["music"]
        elif name == "sound":
            self.settings["sfx"] = not self.settings["sfx"]
        elif name == "screen":
            self.settings["fullscreen"] = not self.settings["fullscreen"]
        elif name == "save":
            self._save()
        elif name == "back":
            self.change_screen("menu")

    def _save(self) -> None:
        """Save the settings and apply the screen mode."""
        save_settings(self.settings)

        if pygame.display.is_fullscreen() != self.settings["fullscreen"]:
            pygame.display.toggle_fullscreen()

        self.message_time = 1.8

    def _item_at(self, position: tuple[int, int]) -> str | None:
        """Return the item under a position."""
        for name, rect in self.rects.items():
            if rect.collidepoint(position):
                return name
        return None

    def on_enter(self) -> None:
        """Discard unsaved changes each time the screen is shown."""
        self.settings = load_settings()
        self.focus = POSITIONS[self.settings["world"]]
        self.message_time = 0.0
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle input."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self._move(-1, 0)
            elif event.key == pygame.K_DOWN:
                self._move(1, 0)
            elif event.key == pygame.K_LEFT:
                self._move(0, -1)
            elif event.key == pygame.K_RIGHT:
                self._move(0, 1)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._activate(self.focus_name)
            elif event.key == pygame.K_ESCAPE:
                self.change_screen("menu")

        elif event.type == pygame.MOUSEMOTION:
            name = self._item_at(event.pos)
            if name is not None:
                self.focus = POSITIONS[name]

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            name = self._item_at(event.pos)
            if name is not None:
                self.focus = POSITIONS[name]
                self._activate(name)

    def update(self, dt: float) -> None:
        """Update the saved message timer."""
        if self.message_time > 0:
            self.message_time = max(0.0, self.message_time - dt)

    # -------------------------
    # Drawing
    # -------------------------

    def _slot_center(self, name: str) -> tuple[int, int]:
        """Return the center of the toggle slot inside a bar."""
        rect = self.rects[name]
        center_x_ratio = self.slots[name][0]
        return (
            round(rect.x + rect.width * center_x_ratio),
            rect.centery,
        )

    def _draw_dropdown(self) -> None:
        """Draw the screen mode selector."""
        bar = self.rects["screen"]
        ratio_x, ratio_w = self.slots["screen"]

        box = pygame.Rect(0, 0, 0, 0)
        box.size = (
            round(bar.width * ratio_w),
            round(bar.height * SCREEN_SLOT_H),
        )
        box.center = self._slot_center("screen")

        pygame.draw.rect(
            self.surface,
            DROPDOWN_FILL,
            box,
            border_radius=box.height // 3,
        )
        pygame.draw.rect(
            self.surface,
            DROPDOWN_BORDER,
            box,
            width=2,
            border_radius=box.height // 3,
        )

        label = "FULLSCREEN" if self.settings["fullscreen"] else "WINDOWED"
        text = self.dropdown_font.render(label, True, TEXT_COLOR)

        arrow_size = max(6, box.height // 4)
        max_text_width = box.width - arrow_size * 3
        if text.get_width() > max_text_width:
            text = pygame.transform.smoothscale(
                text,
                (
                    max_text_width,
                    round(text.get_height() * max_text_width / text.get_width()),
                ),
            )

        text_rect = text.get_rect(
            midleft=(box.left + arrow_size, box.centery),
        )
        self.surface.blit(text, text_rect)

        arrow_x = box.right - arrow_size * 1.6
        pygame.draw.polygon(
            self.surface,
            TEXT_COLOR,
            [
                (arrow_x - arrow_size / 2, box.centery - arrow_size / 3),
                (arrow_x + arrow_size / 2, box.centery - arrow_size / 3),
                (arrow_x, box.centery + arrow_size / 3),
            ],
        )

    def render(self) -> None:
        """Draw the screen."""
        self.surface.blit(self.background, (0, 0))

        # العالمان
        for name in ("ice", "cosmic"):
            chosen = self.settings["world"] == name
            image = self.world_images[(name, chosen)]
            self.surface.blit(
                image,
                image.get_rect(center=self.rects[name].center),
            )

        # الأشرطة والمفاتيح
        for name in ("music", "sound", "screen"):
            self.surface.blit(self.bar_images[name], self.rects[name])

        for name, key in (("music", "music"), ("sound", "sfx")):
            toggle = self.toggle_images[(name, self.settings[key])]
            self.surface.blit(
                toggle,
                toggle.get_rect(center=self._slot_center(name)),
            )

        self._draw_dropdown()

        # إطار التركيز للعناصر غير الأزرار
        if self.focus_name not in self.buttons:
            pygame.draw.rect(
                self.surface,
                FOCUS_COLOR,
                self.rects[self.focus_name].inflate(10, 10),
                width=3,
                border_radius=16,
            )

        # الأزرار السفلية
        for name, button in self.buttons.items():
            button.set_selected(self.focus_name == name)
            button.render(self.surface)

        if self.message_time > 0:
            self.surface.blit(
                self.message_surface,
                self.message_surface.get_rect(center=self.message_center),
            )