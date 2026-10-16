import pygame

from src.entities.pacman import Pacman
from src.ui.graphics import GameplayGraphics
from src.systems.level import Level


pygame.init()
surface = pygame.display.set_mode((1200, 800))
clock = pygame.time.Clock()

level = Level(1)
tile = level.fit_to(surface.get_size())
graphics = GameplayGraphics(tile, surface.get_size(), "ice")
pacman = Pacman(level)
score = 0

running = True
while running:
    dt = clock.tick(60) / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        pacman.handle_event(event)

    points, power = pacman.update(dt)
    score += points
    if level.is_cleared:
        level.next_level()
        pacman.reset()

    surface.blit(graphics.wallpaper, (0, 0))
    level.draw(surface, graphics)
    pacman.draw(surface, graphics)
    pygame.display.set_caption(f"Score {score}  Pellets {level.pellets_left}")
    pygame.display.flip()

pygame.quit()