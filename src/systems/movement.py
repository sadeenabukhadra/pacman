"""Movement system: shared grid movement helpers for Pac-Man and ghosts."""

DIRS = {
    "up": (0, -1),
    "down": (0, 1),
    "left": (-1, 0),
    "right": (1, 0),
}

OPPOSITE = {
    "up": "down",
    "down": "up",
    "left": "right",
    "right": "left",
}

EPSILON = 1e-9


def next_cell(
    col: int,
    row: int,
    direction: str,
) -> tuple[int, int]:
    """Return the cell next to (col, row) in a direction."""
    dx, dy = DIRS[direction]

    return (
        col + dx,
        row + dy,
    )


def can_move(level, col: int, row: int, direction: str) -> bool:
    """Return True if there is no wall between the cell and its neighbor."""
    return level.can_pass(col, row, direction)


def open_directions(
    level,
    col: int,
    row: int,
) -> list[str]:
    """Return every direction that is not blocked by a wall."""
    return [
        direction
        for direction in DIRS
        if can_move(
            level,
            col,
            row,
            direction,
        )
    ]


def is_intersection(
    level,
    col: int,
    row: int,
) -> bool:
    """Return True if there are three or more ways out of a cell."""
    return (
        len(
            open_directions(
                level,
                col,
                row,
            )
        )
        >= 3
    )


def cell_distance_sq(
    a: tuple[int, int],
    b: tuple[int, int],
) -> int:
    """Return the squared distance between two cells."""
    return (
        (a[0] - b[0]) ** 2
        + (a[1] - b[1]) ** 2
    )


def manhattan(
    a: tuple[int, int],
    b: tuple[int, int],
) -> int:
    """Return the Manhattan distance between two cells."""
    return (
        abs(a[0] - b[0])
        + abs(a[1] - b[1])
    )


def advance(
    entity,
    distance: float,
    choose_target,
    on_arrive=None,
) -> None:
    """Move an entity along the grid by a distance in cells."""
    remaining = distance

    while remaining > 0:
        if entity.target is None:
            choose_target()

            if entity.target is None:
                return

        dx, dy = DIRS[
            entity.direction
        ]

        left = (
            (entity.target[0] - entity.x) * dx
            + (entity.target[1] - entity.y) * dy
        )

        step = min(
            remaining,
            max(
                left,
                0.0,
            ),
        )

        entity.x += dx * step
        entity.y += dy * step

        remaining -= step

        if step >= left - EPSILON:
            entity.col, entity.row = (
                entity.target
            )

            entity.x = float(
                entity.col
            )

            entity.y = float(
                entity.row
            )

            entity.target = None

            if on_arrive is not None:
                on_arrive(
                    entity
                )


def reverse(
    entity,
) -> None:
    """Turn an entity around immediately."""
    if entity.target is not None:
        entity.target = (
            entity.col,
            entity.row,
        )

    entity.direction = OPPOSITE[
        entity.direction
    ]