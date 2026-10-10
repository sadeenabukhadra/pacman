import pygame

from src.entities import Ghost, Pacman, Pellet, PowerCrystal


class CollisionSystem:
    def pacman_with_pellet(
        self,
        pacman: Pacman,
        pellet: Pellet,
    ) -> bool:
        return pacman.rect.colliderect(
            pellet.get_rect(),
        )

    def pacman_with_power_crystal(
        self,
        pacman: Pacman,
        crystal: PowerCrystal,
    ) -> bool:
        return pacman.rect.colliderect(
            crystal.get_rect(),
        )

    def pacman_with_ghost(
        self,
        pacman: Pacman,
        ghost: Ghost,
    ) -> bool:
        return pacman.rect.colliderect(
            ghost.rect,
        )

    def get_eaten_pellets(
        self,
        pacman: Pacman,
        pellets: list[Pellet],
    ) -> list[Pellet]:
        eaten: list[Pellet] = []

        for pellet in pellets:
            if (
                not pellet.is_eaten()
                and self.pacman_with_pellet(pacman, pellet)
            ):
                eaten.append(pellet)

        return eaten

    def get_eaten_crystals(
        self,
        pacman: Pacman,
        crystals: list[PowerCrystal],
    ) -> list[PowerCrystal]:
        eaten: list[PowerCrystal] = []

        for crystal in crystals:
            if (
                not crystal.is_eaten()
                and self.pacman_with_power_crystal(
                    pacman,
                    crystal,
                )
            ):
                eaten.append(crystal)

        return eaten

    def get_colliding_ghosts(
        self,
        pacman: Pacman,
        ghosts: list[Ghost],
    ) -> list[Ghost]:
        collided: list[Ghost] = []

        for ghost in ghosts:
            if self.pacman_with_ghost(
                pacman,
                ghost,
            ):
                collided.append(ghost)

        return collided