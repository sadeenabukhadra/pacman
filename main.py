"""Entry point of the Pac-Man game."""

import pygame

from mazegenerator.mazegenerator import MazeGenerator

from src.managers.asset_manager import AssetManager
from src.managers.screen_manager import ScreenManager
from src.managers.settings_manager import load_settings
from src.maze.maze import Maze
from src.screens.gameplay_screen import GameplayScreen
from src.screens.high_scores_screen import HighScoresScreen
from src.screens.instructions_screen import InstructionsScreen
from src.screens.menu_screen import MenuScreen
from src.screens.settings_screen import SettingsScreen
from src.themes.theme_manager import ThemeManager


WIDTH = 1200
HEIGHT = 800
FPS = 60


def create_first_maze() -> Maze:
    """Create the first maze using the assigned generator.

    Returns:
        Generated maze.

    Raises:
        RuntimeError: If maze generation fails.
    """
    try:
        generator = MazeGenerator(
            size=(15, 15),
            perfect=False,
            seed=42,
        )

        return Maze(generator.maze)

    except Exception as error:
        raise RuntimeError(
            f"Failed to generate maze: {error}"
        ) from error


def main() -> None:
    """Run the game."""
    pygame.init()

    settings = load_settings()

    flags = pygame.SCALED

    if settings["fullscreen"]:
        flags |= pygame.FULLSCREEN

    surface = pygame.display.set_mode(
        (WIDTH, HEIGHT),
        flags,
    )

    pygame.display.set_caption("Pac-Man")

    clock = pygame.time.Clock()

    # -------------------------
    # Managers
    # -------------------------

    screen_manager = ScreenManager()

    change = screen_manager.change_screen

    selected_theme = settings.get(
        "world",
        "ice",
    )

    theme_manager = ThemeManager(
        selected_theme
    )

    asset_manager = AssetManager()

    # -------------------------
    # Reused screens
    # -------------------------

    settings_screen = SettingsScreen(
        surface=surface,
        theme_manager=theme_manager,
        change_screen=change,
    )

    # -------------------------
    # Register menu
    # -------------------------

    screen_manager.register(
        "menu",
        lambda: MenuScreen(
            surface,
            change,
        ),
    )

    # -------------------------
    # Register instructions
    # -------------------------

    screen_manager.register(
        "instructions",
        lambda: InstructionsScreen(
            surface,
            change,
        ),
    )

    # -------------------------
    # Register high scores
    # -------------------------

    screen_manager.register(
        "high_scores",
        lambda: HighScoresScreen(
            surface,
            change,
        ),
    )

    # -------------------------
    # Register settings
    # -------------------------

    screen_manager.register(
        "settings",
        lambda: settings_screen,
    )

    # -------------------------
    # Register gameplay
    # -------------------------

    def create_gameplay_screen() -> GameplayScreen:
        """Create a new gameplay screen."""
        maze = create_first_maze()

        return GameplayScreen(
            surface=surface,
            maze=maze,
            theme_manager=theme_manager,
            asset_manager=asset_manager,
        )

    screen_manager.register(
        "gameplay",
        create_gameplay_screen,
    )

    # -------------------------
    # Start game
    # -------------------------

    change("menu")

    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0

        # -------------------------
        # Events
        # -------------------------

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue

            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_F11
            ):
                pygame.display.toggle_fullscreen()
                continue

            if screen_manager.current_screen is not None:
                screen_manager.current_screen.handle_event(
                    event
                )

        # -------------------------
        # Update
        # -------------------------

        if screen_manager.current_screen is not None:
            screen_manager.current_screen.update(
                dt
            )

        # -------------------------
        # Render
        # -------------------------

        if screen_manager.current_screen is not None:
            screen_manager.current_screen.render()

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()