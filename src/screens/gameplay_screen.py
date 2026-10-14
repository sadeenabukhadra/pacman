"""Gameplay screen for displaying the active Pac-Man level."""

import pygame

from src.managers.asset_manager import AssetManager
from src.maze.maze import Maze
from src.rendering.maze_renderer import MazeRenderer
from src.screens.base_screen import BaseScreen
from src.themes.theme_manager import ThemeManager   


class GameplayScreen(BaseScreen):
    """Display and update the active Pac-Man game level."""

    HUD_HEIGHT = 100
    MAZE_MARGIN = 30

    def __init__(
        self,
        surface: pygame.Surface,
        maze: Maze,
        theme_manager: ThemeManager,
        asset_manager: AssetManager,
    ) -> None:
        """Initialize the gameplay screen.

        Args:
            surface: Main Pygame display surface.
            maze: Maze used by the current level.
            theme_manager: Manager containing the active theme.
            asset_manager: Manager responsible for graphical assets.
        """
        super().__init__(surface)

        self.maze = maze
        self.theme_manager = theme_manager
        self.asset_manager = asset_manager

        self.score = 0
        self.lives = 3
        self.level = 1
        self.remaining_time = 90

        self._load_current_theme()

        cell_size, offset_x, offset_y = self._calculate_maze_layout()

        self.maze_renderer = MazeRenderer(
            surface=self.surface,
            asset_manager=self.asset_manager,
            cell_size=cell_size,
            offset_x=offset_x,
            offset_y=offset_y,
        )

        self.font = pygame.font.Font(None, 30)

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle gameplay input events.

        Args:
            event: Pygame event received from the game loop.
        """
        if event.type == pygame.KEYDOWN:
            self._handle_keydown(event)

    def update(self, dt: float) -> None:
        """Update gameplay state.

        Args:
            dt: Time elapsed since the previous frame in seconds.
        """
        self._update_theme()

        if self.remaining_time > 0:
            self.remaining_time = max(
                0,
                self.remaining_time - dt,
            )

    def render(self) -> None:
        """Render the gameplay screen."""
        self.surface.fill((0, 0, 0))

        self._draw_background()
        self._draw_hud()

        self.maze_renderer.render(
            self.maze,
        )

    def set_score(self, score: int) -> None:
        """Update the displayed score.

        Args:
            score: Current player score.
        """
        self.score = max(0, score)

    def set_lives(self, lives: int) -> None:
        """Update the displayed number of lives.

        Args:
            lives: Remaining player lives.
        """
        self.lives = max(0, lives)

    def set_level(self, level: int) -> None:
        """Update the displayed level number.

        Args:
            level: Current level number.
        """
        self.level = max(1, level)

    def set_remaining_time(self, remaining_time: float) -> None:
        """Update the displayed remaining level time.

        Args:
            remaining_time: Remaining time in seconds.
        """
        self.remaining_time = max(
            0,
            remaining_time,
        )

    def set_maze(self, maze: Maze) -> None:
        """Replace the currently displayed maze.

        Args:
            maze: New maze for the current level.
        """
        self.maze = maze

        cell_size, offset_x, offset_y = (
            self._calculate_maze_layout()
        )

        self.maze_renderer = MazeRenderer(
            surface=self.surface,
            asset_manager=self.asset_manager,
            cell_size=cell_size,
            offset_x=offset_x,
            offset_y=offset_y,
        )

    def _handle_keydown(
        self,
        event: pygame.event.Event,
    ) -> None:
        """Handle keyboard presses.

        Args:
            event: Pygame key-down event.
        """
        if event.key == pygame.K_ESCAPE:
            return

        # Pac-Man movement will be connected here later.
        #
        # Example:
        #
        # if event.key in (pygame.K_UP, pygame.K_w):
        #     self.pacman.request_direction(NORTH)
        #
        # Movement is intentionally not implemented here yet because
        # it belongs to the movement/entity system.

    def _load_current_theme(self) -> None:
        """Load assets belonging to the current theme."""
        self.asset_manager.load_theme(
            self.theme_manager.current_theme,
        )

    def _update_theme(self) -> None:
        """Reload assets when the selected theme changes."""
        current_name = (
            self.theme_manager.current_theme.get_name()
        )

        if self.asset_manager.theme_name == current_name:
            return

        self.asset_manager.load_theme(
            self.theme_manager.current_theme,
        )

    def _calculate_maze_layout(
        self,
    ) -> tuple[int, int, int]:
        """Calculate cell size and maze screen position.

        Returns:
            Tuple containing cell size, x offset and y offset.
        """
        screen_width = self.surface.get_width()
        screen_height = self.surface.get_height()

        available_width = (
            screen_width
            - self.MAZE_MARGIN * 2
        )

        available_height = (
            screen_height
            - self.HUD_HEIGHT
            - self.MAZE_MARGIN * 2
        )

        cell_width = (
            available_width // self.maze.width
        )

        cell_height = (
            available_height // self.maze.height
        )

        cell_size = min(
            cell_width,
            cell_height,
        )

        if cell_size <= 0:
            raise ValueError(
                "Screen is too small to render the maze."
            )

        maze_pixel_width = (
            self.maze.width * cell_size
        )

        maze_pixel_height = (
            self.maze.height * cell_size
        )

        offset_x = (
            screen_width - maze_pixel_width
        ) // 2

        gameplay_height = (
            screen_height - self.HUD_HEIGHT
        )

        offset_y = (
            self.HUD_HEIGHT
            + (
                gameplay_height
                - maze_pixel_height
            ) // 2
        )

        return (
            cell_size,
            offset_x,
            offset_y,
        )

    def _draw_background(self) -> None:
        """Draw a dark background behind HUD and maze."""
        self.surface.fill(
            (4, 8, 20),
        )

    def _draw_hud(self) -> None:
        """Draw the gameplay HUD."""
        if self.asset_manager.has_image(
            "hud_panel"
        ):
            self._draw_hud_panel()

        self._draw_hud_text()

    def _draw_hud_panel(self) -> None:
        """Draw the themed HUD panel image."""
        source = self.asset_manager.get_image(
            "hud_panel"
        )

        width = self.surface.get_width()
        height = self.HUD_HEIGHT

        panel = pygame.transform.smoothscale(
            source,
            (width, height),
        )

        self.surface.blit(
            panel,
            (0, 0),
        )

    def _draw_hud_text(self) -> None:
        """Draw score, lives, level and remaining time."""
        screen_width = self.surface.get_width()

        labels = (
            f"SCORE  {self.score}",
            f"LIVES  {self.lives}",
            f"LEVEL  {self.level}",
            f"TIME  {int(self.remaining_time)}",
        )

        section_width = (
            screen_width // len(labels)
        )

        for index, label in enumerate(labels):
            text = self.font.render(
                label,
                True,
                (235, 250, 255),
            )

            center_x = (
                section_width * index
                + section_width // 2
            )

            rect = text.get_rect(
                center=(
                    center_x,
                    self.HUD_HEIGHT // 2,
                )
            )

            self.surface.blit(
                text,
                rect,
            )