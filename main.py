"""Entry point of the Pac-Man game."""

import pygame

from mazegenerator.mazegenerator import MazeGenerator

from src.managers.asset_manager import AssetManager
from src.managers.screen_manager import ScreenManager
from src.managers.settings_manager import load_settings
from src.maze.maze import Maze
from src.screens.game_over_screen import GameOverScreen
from src.screens.game_win_screen import GameWinScreen
from src.screens.gameplay_screen import GameplayScreen
from src.screens.high_scores_screen import HighScoresScreen
from src.screens.instructions_screen import InstructionsScreen
from src.screens.menu_screen import MenuScreen
from src.screens.settings_screen import SettingsScreen
from src.themes.theme_manager import ThemeManager


WIDTH = 1200
HEIGHT = 800
FPS = 60
STARTING_LIVES = 3
LEVEL_MAX_TIME = 90.0


def create_first_maze() -> Maze:
    """Generate the first maze, reporting generator errors clearly."""
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
    """Run the screens and connect gameplay to the result screens."""
    pygame.init()

    try:
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

        screen_manager = ScreenManager()
        change = screen_manager.change_screen

        theme_manager = ThemeManager(
            settings.get("world", "ice")
        )
        asset_manager = AssetManager()

        final_score = 0

        settings_screen = SettingsScreen(
            surface=surface,
            theme_manager=theme_manager,
            change_screen=change,
        )

        screen_manager.register(
            "menu",
            lambda: MenuScreen(surface, change),
        )

        screen_manager.register(
            "instructions",
            lambda: InstructionsScreen(surface, change),
        )

        screen_manager.register(
            "high_scores",
            lambda: HighScoresScreen(surface, change),
        )

        screen_manager.register(
            "settings",
            lambda: settings_screen,
        )

        def show_game_over(score: int) -> None:
            """Save the final score and open the loss screen."""
            nonlocal final_score
            final_score = score
            change("game_over")

        def show_game_win(score: int) -> None:
            """Save the final score and open the victory screen."""
            nonlocal final_score
            final_score = score
            change("game_win")

        screen_manager.register(
            "game_over",
            lambda: GameOverScreen(
                surface=surface,
                change_screen=change,
                score=final_score,
            ),
        )

        screen_manager.register(
            "game_win",
            lambda: GameWinScreen(
                surface=surface,
                change_screen=change,
                score=final_score,
            ),
        )

        def create_gameplay_screen() -> GameplayScreen:
            """Create a fresh run when Start or Play Again is selected."""
            return GameplayScreen(
                surface=surface,
                maze=create_first_maze(),
                theme_manager=theme_manager,
                asset_manager=asset_manager,
                on_game_over=show_game_over,
                lives=STARTING_LIVES,
                level_max_time=LEVEL_MAX_TIME,
                on_game_win=show_game_win,
            )

        screen_manager.register(
            "gameplay",
            create_gameplay_screen,
        )

        change("menu")
        running = True

        while running:
            dt = clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break

                if (
                    event.type == pygame.KEYDOWN
                    and event.key == pygame.K_F11
                ):
                    pygame.display.toggle_fullscreen()
                    continue

                if screen_manager.current_screen is not None:
                    screen_manager.current_screen.handle_event(event)

            if not running:
                break

            if screen_manager.current_screen is not None:
                screen_manager.current_screen.update(dt)

            if screen_manager.current_screen is not None:
                screen_manager.current_screen.render()

            pygame.display.flip()

    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
