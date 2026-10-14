"""Load and serve every gameplay graphic."""

from pathlib import Path

import pygame


IMAGE_DIR = Path("images")
TRIM_ALPHA = 20

DIRECTIONS = (
    "up",
    "down",
    "left",
    "right",
)

WORLDS = (
    "ice",
    "cosmic",
)

GHOST_COLORS = (
    "red",
    "pink",
    "blue",
    "yellow",
)

WALL_PIECES = (
    "horizontal",
    "vertical",
    "corner",
    "t_junction",
    "cross",
    "end",
    "single",
)


# ==========================================================
# Gameplay image paths
# ==========================================================

PACMAN_PATHS = {
    direction: (
        IMAGE_DIR
        / "pacman"
        / f"pacman_{direction}.png"
    )
    for direction in DIRECTIONS
}

PACGUM_PATH = (
    IMAGE_DIR
    / "pac_gum"
    / "pacgum.png"
)

SUPER_PACGUM_PATHS = {
    world: (
        IMAGE_DIR
        / "pac_gum"
        / f"superpacgum_{world}.png"
    )
    for world in WORLDS
}


GHOST_PATHS = {
    (color, direction): (
        IMAGE_DIR
        / "ghosts"
        / f"ghost_{color}"
        / f"ghost_{color}_{direction}.png"
    )
    for color in GHOST_COLORS
    for direction in DIRECTIONS
}


EYES_PATHS = {
    direction: (
        IMAGE_DIR
        / "eyes"
        / f"eyes_{direction}.png"
    )
    for direction in DIRECTIONS
}


FRIGHTENED_PATHS = {
    "left": (
        IMAGE_DIR
        / "ghost_frightened"
        / "ghost_frightened_left.png"
    ),
    "right": (
        IMAGE_DIR
        / "ghost_frightened"
        / "ghost_frightened_right.png"
    ),
}


FRIGHTENED_FLASH_PATHS = {
    "left": (
        IMAGE_DIR
        / "ghost_frightened"
        / "frightened_flash_left.png"
    ),
    "right": (
        IMAGE_DIR
        / "ghost_frightened"
        / "frightened_flash_right.png"
    ),
}


LIFE_ICON_PATH = (
    IMAGE_DIR
    / "life_icon.png"
)


WALLPAPER_PATHS = {
    "ice": (
        IMAGE_DIR
        / "theme"
        / "wallpaper_ice.png"
    ),
    "cosmic": (
        IMAGE_DIR
        / "theme"
        / "wallpaper_cosmic.png"
    ),
}


GAME_OVER_PATHS = {
    "ice": (
        IMAGE_DIR
        / "gameover_ice.png"
    ),
    "cosmic": (
        IMAGE_DIR
        / "gameover_cosmic.png"
    ),
}


# ==========================================================
# Wall paths
# ==========================================================

WALL_THEME_DIRS = {
    "ice": (
        IMAGE_DIR
        / "wall"
        / "ice_theme"
    ),
    "cosmic": (
        IMAGE_DIR
        / "wall"
        / "cosmic_theme"
    ),
}


WALL_PATHS = {
    (
        "ice",
        "horizontal",
    ): (
        WALL_THEME_DIRS["ice"]
        / "wall_horizontal_ice.png"
    ),

    (
        "ice",
        "vertical",
    ): (
        WALL_THEME_DIRS["ice"]
        / "wall_vertical_ice.png"
    ),

    (
        "ice",
        "corner",
    ): (
        WALL_THEME_DIRS["ice"]
        / "wall_corner_ice.png"
    ),

    (
        "ice",
        "t_junction",
    ): (
        WALL_THEME_DIRS["ice"]
        / "wall_t_junction_ice.png"
    ),

    (
        "ice",
        "cross",
    ): (
        WALL_THEME_DIRS["ice"]
        / "wall_cross_ice.png"
    ),

    (
        "ice",
        "end",
    ): (
        WALL_THEME_DIRS["ice"]
        / "wall_end_ice.png"
    ),

    (
        "ice",
        "single",
    ): (
        WALL_THEME_DIRS["ice"]
        / "wall_single_ice.png"
    ),

    (
        "cosmic",
        "horizontal",
    ): (
        WALL_THEME_DIRS["cosmic"]
        / "wall_horizontal_cosmic.png"
    ),

    (
        "cosmic",
        "vertical",
    ): (
        WALL_THEME_DIRS["cosmic"]
        / "wall_vertical_cosmic.png"
    ),

    (
        "cosmic",
        "corner",
    ): (
        WALL_THEME_DIRS["cosmic"]
        / "wall_corner_cosmic.png"
    ),

    (
        "cosmic",
        "t_junction",
    ): (
        WALL_THEME_DIRS["cosmic"]
        / "wall_t_junction_cosmic.png"
    ),

    (
        "cosmic",
        "cross",
    ): (
        WALL_THEME_DIRS["cosmic"]
        / "wall_cross_cosmic.png"
    ),

    (
        "cosmic",
        "end",
    ): (
        WALL_THEME_DIRS["cosmic"]
        / "wall_end_cosmic.png"
    ),

    (
        "cosmic",
        "single",
    ): (
        WALL_THEME_DIRS["cosmic"]
        / "wall_single_cosmic.png"
    ),
}


# ==========================================================
# Wall rotation
# ==========================================================

CLOCKWISE = {
    "N": "E",
    "E": "S",
    "S": "W",
    "W": "N",
}


BASE_CONNECTIONS = {
    "end": {
        "ice": {"S"},
        "cosmic": {"S"},
    },

    "corner": {
        "ice": {"N", "E"},
        "cosmic": {"N", "E"},
    },

    "t_junction": {
        "ice": {"W", "E", "S"},
        "cosmic": {"W", "E", "S"},
    },
}


# ==========================================================
# Image helpers
# ==========================================================


def _load(
    path: Path,
    trim: bool = True,
) -> pygame.Surface:
    """Load an image with transparency."""

    if not path.exists():
        raise FileNotFoundError(
            f"Image not found: {path}"
        )

    image = pygame.image.load(
        str(path)
    ).convert_alpha()

    if trim:
        bounds = image.get_bounding_rect(
            min_alpha=TRIM_ALPHA
        )

        if bounds.width > 0 and bounds.height > 0:
            image = image.subsurface(
                bounds
            ).copy()

    return image


def _fit_box(
    image: pygame.Surface,
    box: int,
) -> pygame.Surface:
    """Fit an image inside a square."""

    scale = (
        box
        / max(
            image.get_width(),
            image.get_height(),
        )
    )

    width = max(
        1,
        round(
            image.get_width()
            * scale
        ),
    )

    height = max(
        1,
        round(
            image.get_height()
            * scale
        ),
    )

    return pygame.transform.smoothscale(
        image,
        (
            width,
            height,
        ),
    )


def _fit_height(
    image: pygame.Surface,
    height: int,
) -> pygame.Surface:
    """Scale an image by height."""

    width = round(
        image.get_width()
        * height
        / image.get_height()
    )

    return pygame.transform.smoothscale(
        image,
        (
            width,
            height,
        ),
    )


def _cover(
    image: pygame.Surface,
    size: tuple[int, int],
) -> pygame.Surface:
    """Scale an image to cover the full screen."""

    scale = max(
        size[0] / image.get_width(),
        size[1] / image.get_height(),
    )

    scaled = pygame.transform.smoothscale(
        image,
        (
            round(
                image.get_width()
                * scale
            ),
            round(
                image.get_height()
                * scale
            ),
        ),
    )

    crop = pygame.Rect(
        0,
        0,
        *size,
    )

    crop.center = (
        scaled.get_rect().center
    )

    return scaled.subsurface(
        crop
    ).copy()


# ==========================================================
# Gameplay graphics
# ==========================================================


class GameplayGraphics:
    """Manage gameplay images."""

    def __init__(
        self,
        tile_size: int,
        window_size: tuple[int, int],
        world: str = "ice",
    ) -> None:
        """Load gameplay graphics."""

        if world not in WORLDS:
            raise ValueError(
                f"Unknown world: {world}"
            )

        self.tile = tile_size
        self.window_size = window_size
        self.world = world

        character_size = round(
            tile_size * 0.9
        )

        eyes_size = round(
            character_size * 0.75
        )

        pellet_size = max(
            4,
            round(
                tile_size * 0.28
            ),
        )

        power_size = round(
            tile_size * 0.7
        )

        # Pac-Man
        self.pacman = {
            direction: _fit_box(
                _load(path),
                character_size,
            )
            for direction, path
            in PACMAN_PATHS.items()
        }

        # Ghosts
        self.ghosts = {
            key: _fit_box(
                _load(path),
                character_size,
            )
            for key, path
            in GHOST_PATHS.items()
        }

        # Ghost eyes
        self.eyes = {
            direction: _fit_box(
                _load(path),
                eyes_size,
            )
            for direction, path
            in EYES_PATHS.items()
        }

        # Frightened ghosts
        self.frightened = {
            direction: _fit_box(
                _load(path),
                character_size,
            )
            for direction, path
            in FRIGHTENED_PATHS.items()
        }

        self.frightened_flash = {
            direction: _fit_box(
                _load(path),
                character_size,
            )
            for direction, path
            in FRIGHTENED_FLASH_PATHS.items()
        }

        # Pacgum
        self.pacgum = _fit_box(
            _load(PACGUM_PATH),
            pellet_size,
        )

        # Super Pacgum
        self.super_pacgum = {
            world_name: _fit_box(
                _load(path),
                power_size,
            )
            for world_name, path
            in SUPER_PACGUM_PATHS.items()
        }

        # Life icon
        self.life_icon = _fit_height(
            _load(LIFE_ICON_PATH),
            round(
                tile_size * 0.8
            ),
        )

        # Wallpapers
        self.wallpapers = {
            world_name: _cover(
                _load(
                    path,
                    trim=False,
                ),
                window_size,
            )
            for world_name, path
            in WALLPAPER_PATHS.items()
        }

        # Game over images
        self.game_over = {
            world_name: _cover(
                _load(
                    path,
                    trim=False,
                ),
                window_size,
            )
            for world_name, path
            in GAME_OVER_PATHS.items()
        }

    # ======================================================
    # Theme
    # ======================================================

    def set_world(
        self,
        world: str,
    ) -> None:
        """Change active theme."""

        if world not in WORLDS:
            raise ValueError(
                f"Unknown world: {world}"
            )

        self.world = world

    # ======================================================
    # Pac-Man
    # ======================================================

    def get_pacman(
        self,
        direction: str,
    ) -> pygame.Surface:
        """Return Pac-Man sprite."""

        return self.pacman[
            direction
        ]

    # ======================================================
    # Ghosts
    # ======================================================

    def get_ghost(
        self,
        color: str,
        direction: str,
    ) -> pygame.Surface:
        """Return ghost sprite."""

        return self.ghosts[
            (
                color,
                direction,
            )
        ]

    def get_eyes(
        self,
        direction: str,
    ) -> pygame.Surface:
        """Return ghost eyes."""

        return self.eyes[
            direction
        ]

    def get_frightened(
        self,
        direction: str,
        flashing: bool = False,
    ) -> pygame.Surface:
        """Return frightened ghost."""

        side = (
            "left"
            if direction
            in (
                "left",
                "up",
            )
            else "right"
        )

        source = (
            self.frightened_flash
            if flashing
            else self.frightened
        )

        return source[
            side
        ]

    # ======================================================
    # Properties
    # ======================================================

    @property
    def wallpaper(
        self,
    ) -> pygame.Surface:
        """Return active wallpaper."""

        return self.wallpapers[
            self.world
        ]

    @property
    def super_pellet(
        self,
    ) -> pygame.Surface:
        """Return active Super Pacgum."""

        return self.super_pacgum[
            self.world
        ]

    @property
    def game_over_image(
        self,
    ) -> pygame.Surface:
        """Return active game-over image."""

        return self.game_over[
            self.world
        ]

    # ======================================================
    # Drawing helpers
    # ======================================================

    def blit_center(
        self,
        surface: pygame.Surface,
        image: pygame.Surface,
        center: tuple[int, int],
    ) -> None:
        """Draw image centered."""

        surface.blit(
            image,
            image.get_rect(
                center=center
            ),
        )

    def draw_lives(
        self,
        surface: pygame.Surface,
        lives: int,
        topleft: tuple[int, int],
        gap: int = 6,
    ) -> None:
        """Draw remaining lives."""

        x, y = topleft

        for _ in range(
            lives
        ):
            surface.blit(
                self.life_icon,
                (
                    x,
                    y,
                ),
            )

            x += (
                self.life_icon.get_width()
                + gap
            )