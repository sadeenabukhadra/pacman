"""Load, scale and cache the game images."""

from pathlib import Path

import pygame

IMAGE_ROOT = Path("images")


class AssetManager:
    """Load images once and reuse them."""

    def __init__(self, root: Path = IMAGE_ROOT) -> None:
        """Initialize the manager.

        Args:
            root: Folder that contains the images.
        """
        self.root = root
        self._cache: dict[
            tuple[str, tuple[int, int] | None, int], pygame.Surface
        ] = {}
        self._missing: set[str] = set()

    def load(
        self,
        relative_path: str,
        size: tuple[int, int] | None = None,
        rotation: int = 0,
    ) -> pygame.Surface:
        """Return an image, scaled and rotated, from the cache if possible.

        A missing or broken file gives a magenta placeholder and one
        warning, so the game never crashes because of an image.

        Args:
            relative_path: Path inside the images folder.
            size: Final (width, height), or None to keep the size.
            rotation: Clockwise rotation in degrees (0, 90, 180, 270).

        Returns:
            The prepared surface.
        """
        key = (relative_path, size, rotation % 360)

        if key not in self._cache:
            self._cache[key] = self._prepare(relative_path, size, rotation)

        return self._cache[key]

    def maze_tile(
        self,
        theme: str,
        name: str,
        tile_size: int,
        rotation: int = 0,
    ) -> pygame.Surface:
        """Return a square maze tile of a theme.

        Args:
            theme: Theme folder name ("ice" or "cosmic").
            name: File name without extension, e.g. "wall_corner".
            tile_size: Side of the tile in pixels.
            rotation: Clockwise rotation in degrees.

        Returns:
            The prepared tile.
        """
        return self.load(
            f"maze/{theme}/{name}.png",
            (tile_size, tile_size),
            rotation,
        )

    def _prepare(
        self,
        relative_path: str,
        size: tuple[int, int] | None,
        rotation: int,
    ) -> pygame.Surface:
        """Read one file and apply the size and rotation."""
        try:
            image = pygame.image.load(
                str(self.root / relative_path)
            ).convert_alpha()
        except (pygame.error, OSError):
            if relative_path not in self._missing:
                self._missing.add(relative_path)
                print(f"Warning: cannot load image '{relative_path}'.")
            image = pygame.Surface(size or (32, 32), pygame.SRCALPHA)
            image.fill((255, 0, 255))

        if size is not None and image.get_size() != size:
            image = pygame.transform.smoothscale(image, size)

        if rotation % 360:
            image = pygame.transform.rotate(image, -(rotation % 360))

        return image