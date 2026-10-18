"""Entry point of the Pac-Man game."""

import sys
from time import perf_counter

import pygame

from mazegenerator.mazegenerator import MazeGenerator

from src.config.config_loader import ConfigError, load_config
from src.config.config_validater import GameConfig, config_validator
from src.managers.asset_manager import AssetManager
from src.managers.display_manager import DisplayManager
from src.managers.screen_manager import ScreenManager
from src.managers.settings_manager import load_settings, save_settings
from src.maze.maze import Maze
from src.rendering.entity_renderer import EntityRenderer
from src.screens.result_screen import ResultScreen
from src.managers.score_manager import configure_scores, load_scores
from src.screens.gameplay_screen import GameplayScreen
from src.screens.high_scores_screen import HighScoresScreen
from src.screens.instructions_screen import InstructionsScreen
from src.screens.menu_screen import MenuScreen
from src.screens.settings_screen import SettingsScreen
from src.themes.theme_manager import ThemeManager


WIDTH = 1200
HEIGHT = 800
FPS = 60


def create_first_maze(config: GameConfig) -> Maze:
    """Create the first maze using the assigned generator.

    Args:
        config: Validated settings containing level dimensions and seed.

    Returns:
        Generated maze.

    Raises:
        RuntimeError: If maze generation fails.
    """
    try:
        first_level = config["level"][0]
        generator = MazeGenerator(
            size=(first_level["width"], first_level["height"]),
            perfect=False,
            seed=config["seed"],
        )

        return Maze(generator.maze)

    except Exception as error:
        raise RuntimeError(
            f"Failed to generate maze: {error}"
        ) from error


def run_game(config: GameConfig) -> None:
    """Initialize screens and run the game with validated settings.

    Args:
        config: Configuration shared with the active gameplay screen.
    """
    configure_scores(str(config.get("highscore_filename", "high_scor.json")))
    load_scores()
    pygame.init()

    settings = load_settings()
    display = DisplayManager(settings["fullscreen"])
    # Menus keep their existing 1200x800 layout and mouse coordinates.
    menu_canvas = pygame.Surface((WIDTH, HEIGHT))
    pygame.display.set_caption("Pac-Man")
    clock = pygame.time.Clock()
    screen_manager = ScreenManager()
    theme_manager = ThemeManager(config["theme"])
    asset_manager = AssetManager()
    entity_renderer = EntityRenderer(display.surface, asset_manager)
    start_requested: float | None = None
    first_game_frame = False
    final_score = 0
    final_won = False
    final_background: pygame.Surface | None = None

    def change(name: str) -> None:
        """Restore menu dimensions before creating a non-gameplay screen."""
        nonlocal start_requested, first_game_frame
        if name == "gameplay":
            start_requested = perf_counter()
            first_game_frame = True
        if name != "gameplay":
            display.show_menu()
        screen_manager.change_screen(name)

    def apply_display_mode(enabled: bool) -> None:
        """Apply Settings/F11 modes and preserve an active gameplay run."""
        old_mode = display.fullscreen
        try:
            display.set_fullscreen(enabled)
            current = screen_manager.current_screen
            if isinstance(current, GameplayScreen):
                current.relayout()
        except (pygame.error, ValueError, RuntimeError):
            display.set_fullscreen(old_mode)
            current = screen_manager.current_screen
            if isinstance(current, GameplayScreen):
                current.relayout()
            raise

    screen_manager.register(
        "menu", lambda: MenuScreen(menu_canvas, change),
    )
    screen_manager.register(
        "instructions", lambda: InstructionsScreen(menu_canvas, change),
    )
    screen_manager.register(
        "high_scores", lambda: HighScoresScreen(menu_canvas, change),
    )
    screen_manager.register(
        "settings", lambda: SettingsScreen(
            surface=menu_canvas, theme_manager=theme_manager,
            change_screen=change, on_display_change=apply_display_mode,
        ),
    )

    def show_game_over(score: int) -> None:
        """Capture the finished maze before restoring menu dimensions."""
        nonlocal final_score, final_won, final_background
        current = screen_manager.current_screen
        final_score = score
        if isinstance(current, GameplayScreen):
            final_won = current.won
            final_background = current.surface.copy()
        change("game_over")

    screen_manager.register(
        "game_over", lambda: ResultScreen(
            surface=menu_canvas, change_screen=change, score=final_score,
            won=final_won, background=final_background,
            theme_name=theme_manager.current.name,
        ),
    )

    def create_gameplay() -> GameplayScreen:
        """Start each new run at the standard menu-sized display."""
        started = perf_counter()
        display.show_menu()
        displayed = perf_counter()
        maze = create_first_maze(config)
        generated = perf_counter()
        gameplay = GameplayScreen(
            surface=display.surface, maze=maze,
            theme_manager=theme_manager, asset_manager=asset_manager,
            config=config, on_main_menu=lambda: change("menu"),
            on_restart=lambda: change("gameplay"),
            on_game_over=show_game_over, display_manager=display,
            entity_renderer=entity_renderer,
        )
        prepared = perf_counter()
        print(
            f"[START] Display setup: "
            f"{(displayed - started) * 1000:.1f} ms"
        )
        print(
            f"[START] Maze generation: "
            f"{(generated - displayed) * 1000:.1f} ms"
        )
        print(
            f"[START] Gameplay setup: "
            f"{(prepared - generated) * 1000:.1f} ms"
        )
        return gameplay

    screen_manager.register("gameplay", create_gameplay)
    change("menu")
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                try:
                    apply_display_mode(not display.fullscreen)
                    updated = load_settings()
                    updated["fullscreen"] = display.fullscreen
                    save_settings(updated)
                    current = screen_manager.current_screen
                    if isinstance(current, SettingsScreen):
                        current.settings["fullscreen"] = display.fullscreen
                except (
                    pygame.error, ValueError, RuntimeError, OSError,
                ) as error:
                    print(f"Warning: display mode could not change: {error}")
                continue
            current = screen_manager.current_screen
            if current is not None:
                mapped = event if isinstance(current, GameplayScreen) else (
                    display.canvas_event(event, menu_canvas.get_size())
                )
                if mapped is not None:
                    current.handle_event(mapped)
        current = screen_manager.current_screen
        if current is not None:
            current.update(dt)
        # Updating can switch screens, so fetch the new one before rendering.
        current = screen_manager.current_screen
        if current is not None:
            rendering_started = perf_counter()
            current.render()
            if first_game_frame and isinstance(current, GameplayScreen):
                elapsed = (perf_counter() - rendering_started) * 1000
                print(f"[START] First gameplay render: {elapsed:.1f} ms")
            if not isinstance(current, GameplayScreen):
                display.present_canvas(menu_canvas)
        pygame.display.flip()
        if (
            first_game_frame and start_requested is not None
            and isinstance(current, GameplayScreen)
        ):
            elapsed = (perf_counter() - start_requested) * 1000
            print(f"[START] Total until first frame: {elapsed:.1f} ms")
            first_game_frame = False
            start_requested = None


def main() -> int:
    """Load exactly one JSON config and report expected errors cleanly.

    Returns:
        Zero on normal exit, or one on invalid usage or a startup error.
    """
    if len(sys.argv) != 2:
        print(
            f"Usage: python {sys.argv[0]} config.json",
            file=sys.stderr,
        )
        return 1
    try:
        config = config_validator(load_config(sys.argv[1]))
        run_game(config)
    except (
        ConfigError, OSError, ValueError, RuntimeError, pygame.error,
    ) as error:
        print(f"Pac-Man error: {error}", file=sys.stderr)
        return 1
    finally:
        pygame.quit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
