"""Render connected, rounded maze walls using the current theme texture.

Geometry comes exclusively from Maze; this module never changes collisions,
the generator, or the reserved cells. Wall outlines are applied to the UNION
of all pieces, so there are no borders between neighbouring wall tiles.
"""

import pygame

from src.managers.asset_manager import AssetManager
from src.maze.maze import EAST, NORTH, SOUTH, WEST, Maze
from src.themes.theme_manager import ThemeManager


WALL_THICKNESS = 0.68
FRAME_THICKNESS = 0.90
DIGIT_MARGIN = 0.42
DIGIT_CORNER_RADIUS = 0.48
FLOOR_BRIGHTNESS = 0.48
ANTIALIAS = 2
ROTATION_OFFSET: dict[str, int] = {}  # Compatibility with older test scripts.
DIRECTIONS = ((0, -1, NORTH), (1, 0, EAST),
              (0, 1, SOUTH), (-1, 0, WEST))
WHITE = (255, 255, 255, 255)


def _tint(mask: pygame.Surface, color: tuple[int, int, int, int]
          ) -> pygame.Surface:
    """Color an alpha mask without changing its silhouette."""
    result = mask.copy()
    result.fill(color, special_flags=pygame.BLEND_RGBA_MULT)
    return result


def _inset(mask: pygame.Surface, pixels: int) -> pygame.Surface:
    """Erode a mask to create one continuous inside edge."""
    result = mask.copy()
    for dx, dy in ((-pixels, 0), (pixels, 0),
                   (0, -pixels), (0, pixels)):
        shifted = pygame.Surface(mask.get_size(), pygame.SRCALPHA)
        shifted.blit(mask, (dx, dy))
        result.blit(shifted, (0, 0),
                    special_flags=pygame.BLEND_RGBA_MIN)
    return result


class MazeRenderer:
    """Cache an antialiased maze while retaining tile position helpers."""

    def __init__(
        self,
        surface: pygame.Surface,
        maze: Maze,
        theme_manager: ThemeManager,
        asset_manager: AssetManager,
        area: pygame.Rect | None = None,
        draw_background: bool = True,
    ) -> None:
        """Fit the existing expanded Maze grid into the requested area."""
        if maze.width < 1 or maze.height < 1:
            raise ValueError("Cannot render an empty maze.")
        self.surface = surface
        self.maze = maze
        self.theme_manager = theme_manager
        self.asset_manager = asset_manager
        self.area = surface.get_rect() if area is None else area.copy()
        if self.area.width < maze.width or self.area.height < maze.height:
            raise ValueError("The drawing area is too small for this maze.")
        self.draw_background = draw_background
        self.tile_size = min(self.area.width // maze.width,
                             self.area.height // maze.height)
        self.origin = (
            self.area.centerx - self.tile_size * maze.width // 2,
            self.area.centery - self.tile_size * maze.height // 2,
        )
        self._built_theme = ""
        self._maze_image: pygame.Surface | None = None
        self._background: pygame.Surface | None = None
        self._digit_mask: pygame.Surface | None = None

    def tile_rect(self, x: int, y: int) -> pygame.Rect:
        """Return a tile rectangle in window coordinates."""
        return pygame.Rect(self.origin[0] + x * self.tile_size,
                           self.origin[1] + y * self.tile_size,
                           self.tile_size, self.tile_size)

    def tile_center(self, x: int, y: int) -> tuple[int, int]:
        """Return the position used to place actors and pellets."""
        return self.tile_rect(x, y).center

    def invalidate(self) -> None:
        """Rebuild after changing maze cells or theme assets in place."""
        self._maze_image = None
        self._built_theme = ""

    def rotate_piece(self, name: str, degrees: int = 90) -> None:
        """Retain legacy controls; wall directions now come from Maze."""
        ROTATION_OFFSET[name] = (
            ROTATION_OFFSET.get(name, 0) + degrees
        ) % 360
        self.invalidate()

    def _geometry(self, tile: int) -> pygame.Surface:
        """Build connected arms with rounded caps, then union solid cells."""
        mask = pygame.Surface((self.maze.width * tile,
                               self.maze.height * tile), pygame.SRCALPHA)
        width = max(2, round(tile * WALL_THICKNESS))
        frame = max(2, round(tile * FRAME_THICKNESS))
        solids = {(x, y)
                  for y in range(1, self.maze.height - 1, 2)
                  for x in range(1, self.maze.width - 1, 2)
                  if self.maze.is_wall(x, y)}
        covered = {(x + dx, y + dy) for x, y in solids
                   for dx in (-1, 0, 1) for dy in (-1, 0, 1)}
        for x, y in self.maze.walls():
            if (x, y) in covered and not self.maze.is_outer(x, y):
                # Retain external wall connections, but remove the old
                # perimeter underneath the now slimmer digit strokes.
                for dx, dy, _ in DIRECTIONS:
                    nx, ny = x + dx, y + dy
                    if ((nx, ny) in covered
                            or not self.maze.in_bounds(nx, ny)
                            or not self.maze.is_wall(nx, ny)):
                        continue
                    sx, sy = min(solids, key=lambda pos:
                                 abs(pos[0] - x) + abs(pos[1] - y))
                    start = (nx * tile + tile // 2,
                             ny * tile + tile // 2)
                    end = ((sx if dx else x) * tile + tile // 2,
                           (sy if dy else y) * tile + tile // 2)
                    pygame.draw.line(mask, WHITE, start, end, width)
                continue
            outer = self.maze.is_outer(x, y)
            thickness = frame if outer else width
            cx, cy = x * tile + tile // 2, y * tile + tile // 2
            radius = thickness // 2
            pygame.draw.circle(mask, WHITE, (cx, cy), radius)
            for dx, dy, _ in DIRECTIONS:
                nx, ny = x + dx, y + dy
                if (not self.maze.in_bounds(nx, ny)
                        or not self.maze.is_wall(nx, ny)):
                    continue
                # Use the smaller width where inner walls meet the frame.
                arm = (frame if outer and self.maze.is_outer(nx, ny)
                       else width)
                half = arm // 2
                if dx:
                    start = cx if dx > 0 else x * tile
                    end = (x + 1) * tile if dx > 0 else cx
                    rect = pygame.Rect(start, cy - half,
                                       end - start + 1, arm)
                else:
                    start = cy if dy > 0 else y * tile
                    end = (y + 1) * tile if dy > 0 else cy
                    rect = pygame.Rect(cx - half, start,
                                       arm, end - start + 1)
                pygame.draw.rect(mask, WHITE, rect)

        # Odd/odd wall tiles are the reserved solid cells in this Maze API.
        # Their surrounding walls are part of the same silhouette, not
        # separately outlined blocks. This preserves the generator's "42".
        # Digits have their own proportions: a fuller stroke and softer
        # corners than corridor walls. Keep a margin inside their original
        # occupied tiles, so no part extends into a neighbouring passage.
        margin = max(1, round(tile * DIGIT_MARGIN))
        digits = pygame.Surface(mask.get_size(), pygame.SRCALPHA)
        stroke = 3 * tile - 2 * margin
        for x, y in sorted(solids):
            # Draw entire runs so internal cell corners cannot scallop
            # the edges of the thinner connected strokes.
            for dx, dy in ((2, 0), (0, 2)):
                if (x - dx, y - dy) in solids:
                    continue
                count = 1
                while (x + count * dx, y + count * dy) in solids:
                    count += 1
                rect = pygame.Rect(
                    (x - 1) * tile + margin,
                    (y - 1) * tile + margin,
                    stroke + (count - 1) * dx * tile,
                    stroke + (count - 1) * dy * tile,
                )
                pygame.draw.rect(
                    digits, WHITE, rect,
                    border_radius=max(1, round(tile * 0.35)),
                )
        self._digit_mask = digits
        mask.blit(digits, (0, 0), special_flags=pygame.BLEND_RGBA_MAX)
        return mask

    def _texture(
        self, size: tuple[int, int], tile: int,
        name: str = "wall_straight",
    ) -> pygame.Surface:
        """Reuse the crystal interior of the existing straight-wall image.

        Source margins and the sprite's border are excluded. The same
        texture covers corners, ends, and digits without shrinking sprites.
        No additional image files are required.
        """
        theme = self.theme_manager.current
        source = self.asset_manager.load(theme.maze_path(name))
        box = source.get_bounding_rect(min_alpha=200)
        if box.width < 2 or box.height < 2:
            raise ValueError(f"{name} must contain an opaque texture.")
        # Accept either orientation of the original straight-wall asset.
        if box.height > box.width:
            source = pygame.transform.rotate(source, 90)
            box = source.get_bounding_rect(min_alpha=200)
        crop = pygame.Rect(0, 0, max(1, box.width // 2),
                           max(1, box.height // 2))
        crop.center = box.center
        sample = source.subsurface(crop).copy()
        # Make the interior opaque; the geometry mask owns transparency.
        opaque = pygame.Surface(sample.get_size())
        opaque.fill((35, 140, 200))
        opaque.blit(sample, (0, 0))
        height = max(2, tile)
        width = max(2, min(tile * 8,
                           round(height * crop.width / crop.height)))
        patch = pygame.transform.smoothscale(opaque, (width, height))
        texture = pygame.Surface(size, pygame.SRCALPHA)
        # Mirrored repeats avoid an abrupt wrap in the sampled texture.
        variants = {(a, b): pygame.transform.flip(patch, a, b)
                    for a in (False, True) for b in (False, True)}
        for row, y in enumerate(range(0, size[1], height)):
            for col, x in enumerate(range(0, size[0], width)):
                texture.blit(variants[(bool(col % 2), bool(row % 2))],
                             (x, y))
        return texture

    def _build(self) -> None:
        """Build the floor, textured silhouette, and continuous ice rim."""
        theme = self.theme_manager.current
        tile = self.tile_size * ANTIALIAS
        size = (self.maze.width * tile, self.maze.height * tile)
        floor = self.asset_manager.load(
            theme.maze_path(theme.floor), size,
        ).copy()
        level = round(255 * FLOOR_BRIGHTNESS)
        floor.fill((level, level, level),
                   special_flags=pygame.BLEND_RGB_MULT)
        mask = self._geometry(tile)
        cosmic = theme.name.lower() == "cosmic"
        rim = (220, 205, 255, 255) if cosmic else (207, 250, 255, 255)
        glow = (120, 80, 255, 55) if cosmic else (30, 175, 255, 55)
        halo = _tint(mask, glow)
        offset = ANTIALIAS * 2
        for dx, dy in ((-offset, 0), (offset, 0),
                       (0, -offset), (0, offset)):
            floor.blit(halo, (dx, dy))
        floor.blit(_tint(mask, rim), (0, 0))
        inner = _inset(mask, max(1, round(tile * 0.075)))
        texture = self._texture(size, tile)
        texture.blit(inner, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        floor.blit(texture, (0, 0))
        self._finish_digits(floor, mask, tile)
        # A narrow upper/left highlight adds depth without covering paths.
        shifted = pygame.Surface(size, pygame.SRCALPHA)
        shifted.blit(mask, (ANTIALIAS, ANTIALIAS))
        highlight = mask.copy()
        highlight.blit(shifted, (0, 0),
                       special_flags=pygame.BLEND_RGBA_SUB)
        floor.blit(_tint(highlight, (255, 255, 255, 180)), (0, 0))
        self._maze_image = pygame.transform.smoothscale(
            floor, (self.maze.width * self.tile_size,
                    self.maze.height * self.tile_size),
        )
        self._background = None
        if self.draw_background:
            self._background = self.asset_manager.load(
                theme.maze_path(theme.background), self.surface.get_size(),
            )
        self._built_theme = theme.name

    def _finish_digits(
        self, floor: pygame.Surface, walls: pygame.Surface, tile: int,
    ) -> None:
        """Give only reserved digits a broad bevel and fine ice facets.

        Erosion uses the complete wall union, so connections to neighbouring
        walls stay open and do not receive an artificial dividing outline.
        Every painted pixel is clipped to the original digit silhouette.
        """
        digits = self._digit_mask
        if digits is None:
            return
        base = floor.copy()
        theme = self.theme_manager.current
        cosmic = theme.name.lower() == "cosmic"
        edge = (222, 207, 255, 255) if cosmic else (218, 253, 255, 255)
        bevel = (123, 109, 220, 255) if cosmic else (79, 182, 228, 255)
        floor.blit(_tint(digits, edge), (0, 0))

        middle = _inset(walls, max(1, round(tile * 0.07)))
        middle.blit(digits, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        floor.blit(_tint(middle, bevel), (0, 0))

        inside = _inset(walls, max(2, round(tile * 0.13)))
        inside.blit(digits, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        crystal = self._digit_texture(digits, tile)
        crystal.blit(inside, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        floor.blit(crystal, (0, 0))

        # Upper/left bevel catches light; lower/right retains blue depth.
        shifted = pygame.Surface(walls.get_size(), pygame.SRCALPHA)
        offset = max(1, round(tile * 0.11))
        shifted.blit(walls, (offset, offset))
        shine = walls.copy()
        shine.blit(shifted, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
        shine.blit(digits, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        floor.blit(_tint(shine, (245, 255, 255, 190)), (0, 0))
        self._blend_digit_joins(floor, base, walls, digits, tile)

    @staticmethod
    def _blend_digit_joins(
        floor: pygame.Surface, base: pygame.Surface,
        walls: pygame.Surface, digits: pygame.Surface, tile: int,
    ) -> None:
        """Blend material boundaries at joins, keeping exposed rims crisp.

        A digit boundary inside the wall union is a material transition,
        not an exposed edge. Fade the extra digit finish there so it cannot
        look like a separate plate pasted over the connecting wall.
        """
        distance = max(2, round(tile * 0.55))
        weight = pygame.Surface(digits.get_size(), pygame.SRCALPHA)
        weight.fill((255, 255, 255, 0))
        for step in range(1, 7):
            inset = _inset(digits, max(1, round(distance * step / 6)))
            layer = _tint(inset, (255, 255, 255, round(255 * step / 6)))
            weight.blit(layer, (0, 0),
                        special_flags=pygame.BLEND_RGBA_MAX)
        exposed = digits.copy()
        exposed.blit(_inset(walls, max(1, round(tile * 0.22))),
                     (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
        weight.blit(exposed, (0, 0), special_flags=pygame.BLEND_RGBA_MAX)
        finished = floor.copy().convert_alpha()
        finished.blit(weight, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        floor.blit(base, (0, 0))
        floor.blit(finished, (0, 0))

    def _digit_texture(
        self, digits: pygame.Surface, tile: int,
    ) -> pygame.Surface:
        """Fill the digits directly with the supplied block's interior.

        Exclude the square rim so it does not draw boxes inside the digits.
        Preserve the source colors and orientation with plain repetition.
        """
        theme = self.theme_manager.current
        if theme.block is None:
            return self._texture(digits.get_size(), tile * 2)
        source = self.asset_manager.load(theme.maze_path(theme.block))
        box = source.get_bounding_rect(min_alpha=200)
        if box.width < 4 or box.height < 4:
            raise ValueError("block.png must contain a visible solid core.")
        # The supplied blocks have a bright square rim and transparent
        # padding. Retain the broad interior, excluding that original rim.
        inset_x = max(1, round(box.width * 0.08))
        inset_y = max(1, round(box.height * 0.08))
        core = box.inflate(-2 * inset_x, -2 * inset_y)
        sample = pygame.Surface(core.size)
        sample.fill(theme.fallback_color)
        sample.blit(source, (0, 0), core)
        result = pygame.Surface(digits.get_size(), pygame.SRCALPHA)
        bounds = digits.get_bounding_rect()
        if bounds.width == 0 or bounds.height == 0:
            return result
        # Repeat the user's block interior directly at a fixed scale.
        # Keep its orientation and colors; only the digit mask clips it.
        side = max(8, tile * 3)
        patch = pygame.transform.smoothscale(sample, (side, side))
        for y in range(bounds.top, bounds.bottom, side):
            for x in range(bounds.left, bounds.right, side):
                result.blit(patch, (x, y))
        return result

    def render(self) -> None:
        """Blit cached layers; rebuild only when the theme/maze changes."""
        if (self._maze_image is None
                or self._built_theme != self.theme_manager.current.name):
            self._build()
        if self.draw_background and self._background is not None:
            self.surface.blit(self._background, (0, 0))
        if self._maze_image is not None:
            self.surface.blit(self._maze_image, self.origin)