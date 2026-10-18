"""Describe the look of one world."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:
    """Names of the images and colors of a world.

    Attributes:
        name: Theme name, also the folder name in images/maze.
        floor: File name (without extension) of the floor tile.
        block: Tile used for the solid "42" blocks, or None to use
            the normal wall tiles.
        background: File name of the maze background.
        hud_panel: File name of the HUD panel.
        game_over_image: File name of the game over image.
        fallback_color: Color used when an image is missing.
        wall_color: Color of the bright core of the inner walls.
        glow_color: Color of the glow around the inner walls.
    """

    name: str
    floor: str
    block: str | None
    background: str
    hud_panel: str
    game_over_image: str
    fallback_color: tuple[int, int, int]
    wall_color: tuple[int, int, int] = (200, 240, 255)
    glow_color: tuple[int, int, int] = (80, 170, 255)

    def maze_path(self, file_name: str) -> str:
        """Return the path of a maze image inside the images folder."""
        return f"maze/{self.name}/{file_name}.png"
