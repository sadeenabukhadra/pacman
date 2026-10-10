import pygame

from src.maze import NORTH, EAST, SOUTH, WEST


class InputHandler:
    def get_direction(self, event: pygame.event.Event) -> int | None:
        if event.type != pygame.KEYDOWN:
            return None

        if event.key in (pygame.K_UP, pygame.K_w):
            return NORTH

        if event.key in (pygame.K_RIGHT, pygame.K_d):
            return EAST

        if event.key in (pygame.K_DOWN, pygame.K_s):
            return SOUTH

        if event.key in (pygame.K_LEFT, pygame.K_a):
            return WEST

        return None