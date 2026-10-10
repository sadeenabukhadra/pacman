"""Entry point of the Pac-Man game."""

import pygame

from src.managers.screen_manager import ScreenManager
from src.managers.settings_manager import load_settings
from src.screens.high_scores_screen import HighScoresScreen
from src.screens.instructions_screen import InstructionsScreen
from src.screens.menu_screen import MenuScreen
from src.screens.settings_screen import SettingsScreen

WIDTH = 1200
HEIGHT = 800  # نسبة 3:2
FPS = 60


def main() -> None:
    """Run the game."""
    pygame.init()

    flags = pygame.SCALED
    if load_settings()["fullscreen"]:
        flags |= pygame.FULLSCREEN

    surface = pygame.display.set_mode((WIDTH, HEIGHT), flags)
    pygame.display.set_caption("Pac-Man")

    clock = pygame.time.Clock()
    screen_manager = ScreenManager()
    change = screen_manager.change_screen

    # شاشة الإعدادات ثقيلة: تُبنى مرة واحدة عند التشغيل وتُعاد استخدامها
    settings_screen = SettingsScreen(surface, change)

    screen_manager.register("menu", lambda: MenuScreen(surface, change))
    screen_manager.register(
        "instructions",
        lambda: InstructionsScreen(surface, change),
    )
    screen_manager.register(
        "high_scores",
        lambda: HighScoresScreen(surface, change),
    )
    screen_manager.register("settings", lambda: settings_screen)

    change("menu")

    running = True

    while running:
        dt = clock.tick(FPS) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue

            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                pygame.display.toggle_fullscreen()
                continue

            if screen_manager.current_screen is not None:
                screen_manager.current_screen.handle_event(event)

        if screen_manager.current_screen is not None:
            screen_manager.current_screen.update(dt)
            screen_manager.current_screen.render()

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()