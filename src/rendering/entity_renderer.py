"""Load and draw directional player and ghost sprites."""

from pathlib import Path

import pygame

from src.entities.ghost import Ghost
from src.entities.pacman import Pacman
from src.systems.collectibles import Collectibles
from src.managers.asset_manager import AssetManager
from src.rendering.maze_renderer import MazeRenderer


class EntityRenderer:
    """Cache actor images and draw them using maze tile coordinates."""

    SPRITE_SCALE = 1.50
    GHOST_SCALE = 1.50
    PELLET_SCALE = 0.80
    POWER_SCALE = 1.55

    def __init__(
        self,
        surface: pygame.Surface,
        asset_manager: AssetManager,
    ) -> None:
        """Load player and ghost frames through the shared image cache.

        Args:
            surface: Surface on which the player is drawn.
            asset_manager: Image cache exposing load(path).

        Raises:
            ValueError: If a player image is completely transparent.
        """
        self.surface = surface
        self.asset_manager = asset_manager
        self._frames: dict[tuple[str, bool], pygame.Surface] = {}
        self._scaled: dict[tuple[str, bool, int], pygame.Surface] = {}
        root = Path(__file__).resolve().parents[2] / "images" / "pacman"
        variants = (
            ("left", ""),
            ("right", ""),
            ("up", "left"),
            ("up", "right"),
            ("down", "left"),
            ("down", "right"),
        )
        for direction, gaze in variants:
            frame_direction = f"{direction}_{gaze}" if gaze else direction
            for mouth_open in (True, False):
                mouth_suffix = "" if mouth_open else "_closemouth"
                gaze_suffix = f"_{gaze}" if gaze else ""
                path = root / (
                    f"pacman_{direction}{mouth_suffix}{gaze_suffix}.png"
                )
                image = self.asset_manager.load(str(path))
                bounds = image.get_bounding_rect(min_alpha=1)
                if bounds.width == 0 or bounds.height == 0:
                    raise ValueError(f"Pac-Man image is empty: {path.name}")
                self._frames[(frame_direction, mouth_open)] = (
                    image.subsurface(bounds).copy()
                )
        self._load_ghost_frames()
        self._load_pellet_frames()

    def _load_actor_image(self, path: Path) -> pygame.Surface:
        """Load a sprite and trim its transparent outer margin."""
        image = self.asset_manager.load(str(path))
        bounds = image.get_bounding_rect(min_alpha=1)
        if bounds.width == 0 or bounds.height == 0:
            raise ValueError(f"Actor image is empty: {path.name}")
        return image.subsurface(bounds).copy()

    def _load_ghost_frames(self) -> None:
        """Load colored ghosts, frightened variants and returning eyes."""
        self._ghost_frames: dict[tuple[str, str], pygame.Surface] = {}
        self._ghost_scaled: dict[
            tuple[str, str, int], pygame.Surface
        ] = {}
        root = Path(__file__).resolve().parents[2] / "images"
        for color in ("red", "pink", "blue", "yellow"):
            for direction in ("up", "down", "left", "right"):
                path = (
                    root / "ghosts" / f"ghost_{color}"
                    / f"ghost_{color}_{direction}.png"
                )
                self._ghost_frames[(color, direction)] = (
                    self._load_actor_image(path)
                )
        for direction in ("left", "right"):
            for state, prefix in (
                ("frightened", "ghost_frightened"),
                ("flash", "frightened_flash"),
            ):
                path = root / "ghost_frightened" / f"{prefix}_{direction}.png"
                self._ghost_frames[(state, direction)] = (
                    self._load_actor_image(path)
                )
        for direction in ("up", "down", "left", "right"):
            path = root / "eyes" / f"eyes_{direction}.png"
            self._ghost_frames[("eyes", direction)] = (
                self._load_actor_image(path)
            )

    def _get_frame(
        self, direction: str, mouth_open: bool, size: int,
    ) -> pygame.Surface:
        """Return an aspect-preserving frame cached at the desired size."""
        key = (direction, mouth_open, size)
        if key not in self._scaled:
            source = self._frames[(direction, mouth_open)]
            scale = size / max(source.get_size())
            dimensions = (
                max(1, round(source.get_width() * scale)),
                max(1, round(source.get_height() * scale)),
            )
            self._scaled[key] = pygame.transform.smoothscale(
                source, dimensions,
            )
        return self._scaled[key]

    def render_pacman(
        self, pacman: Pacman, maze_renderer: MazeRenderer,
    ) -> None:
        """Draw the selected frame at the player's interpolated position.

        Args:
            pacman: Player whose coordinates refer to tile centers.
            maze_renderer: Source of tile size and maze screen origin.
        """
        tile_size = maze_renderer.tile_size
        size = max(1, round(tile_size * self.SPRITE_SCALE))
        frame_direction = pacman.direction
        if frame_direction in ("up", "down"):
            gaze = getattr(pacman, "last_horizontal_direction", "right")
            gaze = "left" if gaze == "right" else "right"
            frame_direction = f"{frame_direction}_{gaze}"
        image = self._get_frame(
            frame_direction, pacman.mouth_open, size,
        )
        origin_x, origin_y = maze_renderer.origin
        center = (
            round(origin_x + (pacman.x + 0.5) * tile_size),
            round(origin_y + (pacman.y + 0.5) * tile_size),
        )
        self.surface.blit(image, image.get_rect(center=center))

    def render_ghost(
        self, ghost: Ghost, maze_renderer: MazeRenderer,
    ) -> None:
        """Draw a ghost's directional sprite, fear frame or returning eyes.

        Args:
            ghost: Ghost providing state, direction and tile coordinates.
            maze_renderer: Shared tile size and window origin.
        """
        state: str = ghost.color
        direction: str = ghost.direction
        if ghost.mode == "eaten":
            state = "eyes"
        elif ghost.mode == "frightened":
            state = "flash" if ghost.flashing else "frightened"
            if direction in ("up", "down"):
                direction = ghost.last_horizontal_direction

        tile_size = maze_renderer.tile_size
        size = max(1, round(tile_size * self.GHOST_SCALE))
        key = (state, direction, size)
        if key not in self._ghost_scaled:
            source = self._ghost_frames[(state, direction)]
            scale = size / max(source.get_size())
            dimensions = (
                max(1, round(source.get_width() * scale)),
                max(1, round(source.get_height() * scale)),
            )
            self._ghost_scaled[key] = pygame.transform.smoothscale(
                source, dimensions,
            )
        image = self._ghost_scaled[key]
        origin_x, origin_y = maze_renderer.origin
        center = (
            round(origin_x + (ghost.x + 0.5) * tile_size),
            round(origin_y + (ghost.y + 0.5) * tile_size),
        )
        self.surface.blit(image, image.get_rect(center=center))

    def _load_pellet_frames(self) -> None:
        """Cache the normal pellet and both themed power pellet images."""
        root = Path(__file__).resolve().parents[2] / "images" / "pac_gum"
        files = {
            "normal": "pacgum.png",
            "ice": "superpacgum_ice.png",
            "cosmic": "superpacgum_cosmic.png",
        }
        self._pellet_frames: dict[str, pygame.Surface] = {
            name: self._load_actor_image(root / filename)
            for name, filename in files.items()
        }
        self._pellet_scaled: dict[tuple[str, int], pygame.Surface] = {}

    def _get_pellet_frame(self, name: str, size: int) -> pygame.Surface:
        """Cache a brighter sprite with a fine outline and a soft halo."""
        key = (name, size)
        if key in self._pellet_scaled:
            return self._pellet_scaled[key]
        source = self._pellet_frames[name]
        scale = size / max(source.get_size())
        dimensions = (
            max(1, round(source.get_width() * scale)),
            max(1, round(source.get_height() * scale)),
        )
        image = pygame.transform.smoothscale(source, dimensions)
        image.fill((24, 24, 24), special_flags=pygame.BLEND_RGB_ADD)
        padding = max(2, round(size * 0.15))
        frame = pygame.Surface(
            (size + 2 * padding, size + 2 * padding), pygame.SRCALPHA,
        )
        center = frame.get_rect().center
        colors = {
            "normal": (255, 220, 110),
            "ice": (130, 235, 255),
            "cosmic": (220, 150, 255),
        }
        accent = colors[name]
        radius = max(1, size // 2)
        pygame.draw.circle(frame, (*accent, 24), center, radius + padding)
        pygame.draw.circle(frame, (*accent, 42), center, radius)
        outline = pygame.mask.from_surface(image, 32).to_surface(
            setcolor=(3, 7, 20, 235), unsetcolor=(0, 0, 0, 0),
        )
        position = image.get_rect(center=center)
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            frame.blit(outline, position.move(dx, dy))
        frame.blit(image, position)
        self._pellet_scaled[key] = frame
        return frame

    def render_collectibles(
        self,
        collectibles: Collectibles,
        maze_renderer: MazeRenderer,
        theme_name: str,
    ) -> None:
        """Draw uneaten pellets; call after maze drawing and before actors.

        Args:
            collectibles: Remaining collectibles for the current level.
            maze_renderer: Shared maze-to-window coordinate mapping.
            theme_name: Ice or cosmic power pellet appearance.
        """
        power_theme = theme_name if theme_name in ("ice", "cosmic") else "ice"
        for pellet in collectibles.active_pellets():
            name = power_theme if pellet.is_super else "normal"
            factor = self.POWER_SCALE if pellet.is_super else self.PELLET_SCALE
            minimum = 6 if pellet.is_super else 3
            size = max(minimum, round(maze_renderer.tile_size * factor))
            image = self._get_pellet_frame(name, size)
            center = maze_renderer.tile_center(pellet.x, pellet.y)
            self.surface.blit(image, image.get_rect(center=center))
