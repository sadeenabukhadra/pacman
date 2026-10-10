import random

from src.entities import Ghost, Pacman
from src.maze import NORTH, EAST, SOUTH, WEST
from src.systems.movement import MovementSystem


class GhostAI:
    def __init__(self, movement: MovementSystem) -> None:
        self.movement = movement

    def get_valid_directions(
        self,
        ghost: Ghost,
    ) -> list[int]:
        directions = [
            NORTH,
            EAST,
            SOUTH,
            WEST,
        ]

        valid: list[int] = []

        for direction in directions:
            if self.movement.can_move(
                ghost.rect,
                direction,
            ):
                valid.append(direction)

        return valid

    def choose_random_direction(
        self,
        ghost: Ghost,
    ) -> int:
        valid = self.get_valid_directions(ghost)

        if not valid:
            return ghost.direction

        return random.choice(valid)

    def choose_chase_direction(
        self,
        ghost: Ghost,
        pacman: Pacman,
    ) -> int:
        valid = self.get_valid_directions(ghost)

        if not valid:
            return ghost.direction

        best_direction = valid[0]
        best_distance = float("inf")

        for direction in valid:
            dx, dy = self.movement.get_direction_vector(
                direction,
            )

            next_x = ghost.rect.centerx + dx
            next_y = ghost.rect.centery + dy

            distance = (
                abs(pacman.rect.centerx - next_x)
                + abs(pacman.rect.centery - next_y)
            )

            if distance < best_distance:
                best_distance = distance
                best_direction = direction

        return best_direction

    def choose_frightened_direction(
        self,
        ghost: Ghost,
        pacman: Pacman,
    ) -> int:
        valid = self.get_valid_directions(ghost)

        if not valid:
            return ghost.direction

        best_direction = valid[0]
        best_distance = -1

        for direction in valid:
            dx, dy = self.movement.get_direction_vector(
                direction,
            )

            next_x = ghost.rect.centerx + dx
            next_y = ghost.rect.centery + dy

            distance = (
                abs(pacman.rect.centerx - next_x)
                + abs(pacman.rect.centery - next_y)
            )

            if distance > best_distance:
                best_distance = distance
                best_direction = direction

        return best_direction