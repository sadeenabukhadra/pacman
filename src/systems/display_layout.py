"""Plan complete-maze layouts without exceeding desktop dimensions."""

from dataclasses import dataclass


@dataclass(frozen=True)
class DisplayPlan:
    """Record requested geometry and its actual screen-safe layout."""

    size: tuple[int, int]
    tile_size: int
    required: tuple[int, int]
    available: tuple[int, int]
    limited: bool
    fullscreen: bool


def plan_display(
    maze_size: tuple[int, int],
    preferred_tile: int,
    desktop: tuple[int, int],
    fullscreen: bool,
    hud_height: int = 130,
    margin: int = 4,
    base_size: tuple[int, int] = (1200, 800),
) -> DisplayPlan:
    """Grow windowed layouts, or fit native fullscreen; never crop a maze.

    Windowed mode reserves 32 horizontal and 80 vertical pixels for desktop
    panels and window decorations. Fullscreen uses the full desktop size.
    """
    columns, rows = maze_size
    if min(columns, rows, preferred_tile, *desktop) < 1:
        raise ValueError("Maze, tile and desktop sizes must be positive.")
    available = desktop if fullscreen else (
        max(1, desktop[0] - 32), max(1, desktop[1] - 80),
    )
    required = (
        columns * preferred_tile + 2 * margin,
        rows * preferred_tile + hud_height + 2 * margin,
    )
    size = desktop if fullscreen else (
        min(available[0], max(base_size[0], required[0])),
        min(available[1], max(base_size[1], required[1])),
    )
    fit = min(
        (size[0] - 2 * margin) // columns,
        (size[1] - hud_height - 2 * margin) // rows,
    )
    if fit < 1:
        raise ValueError("The maze cannot fit even at one pixel per tile.")
    return DisplayPlan(
        size=size, tile_size=min(preferred_tile, fit), required=required,
        available=available,
        limited=any(need > limit for need, limit in zip(required, available)),
        fullscreen=fullscreen,
    )
