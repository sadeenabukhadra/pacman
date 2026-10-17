"""Display the maze and control Pac-Man during gameplay."""

import math
from collections.abc import Callable

import pygame

from src.entities.ghost import Ghost
from src.entities.pacman import Pacman
from src.entities.power_crystal import PowerCrystal
from src.managers.asset_manager import AssetManager
from src.maze.maze import Maze
from src.rendering.entity_renderer import EntityRenderer
from src.rendering.maze_renderer import MazeRenderer
from src.screens.base_screen import BaseScreen
from src.systems.collectibles import Collectibles
from src.systems.ghost_ai import GhostColor
from src.themes.theme_manager import ThemeManager


class GameplayScreen(BaseScreen):
    """Coordinate the maze, actors, collectibles and result callbacks."""

    MAZE_MARGIN = 30
    POINTS_PER_GHOST = 200
    UPDATE_STEP = 1.0 / 120.0
    GHOST_EAT_DISTANCE = 0.55
    HIT_DISTANCE = 0.60
    HIT_PAUSE = 1.5
    RESPAWN_IMMUNITY = 1.0

    def __init__(
        self,
        surface: pygame.Surface,
        maze: Maze,
        theme_manager: ThemeManager,
        asset_manager: AssetManager,
        on_game_over: Callable[[int], None] | None = None,
        lives: int = 3,
        level_max_time: float = 90.0,
        on_game_win: Callable[[int], None] | None = None,
    ) -> None:
        """Create a new gameplay session.

        Args:
            surface: Display surface used by the game loop.
            maze: Playable maze shared by drawing and movement.
            theme_manager: Manager providing the selected theme.
            asset_manager: Shared image cache.
            on_game_over: Callback receiving the final score after losing.
            lives: Number of starting lives.
            level_max_time: Available gameplay time in seconds.
            on_game_win: Callback receiving the final score after winning.

        Raises:
            ValueError: If lives or level time are invalid.
        """
        if type(lives) is not int or lives < 1:
            raise ValueError(
                "Starting lives must be a positive integer."
            )

        if not math.isfinite(level_max_time) or level_max_time <= 0:
            raise ValueError(
                "Level time must be positive and finite."
            )

        super().__init__(surface)

        self.maze = maze
        self.theme_manager = theme_manager
        self.asset_manager = asset_manager

        self.on_game_over = on_game_over
        self.on_game_win = on_game_win

        self.won = False
        self.game_over = False

        self._game_win_notified = False
        self._game_over_notified = False

        self.lives = lives
        self.remaining_time = float(level_max_time)

        self._hit_pause_remaining = 0.0
        self._immunity_remaining = 0.0

        area = self.surface.get_rect().inflate(
            -2 * self.MAZE_MARGIN,
            -2 * self.MAZE_MARGIN,
        )

        self.maze_renderer = MazeRenderer(
            surface=self.surface,
            maze=self.maze,
            theme_manager=self.theme_manager,
            asset_manager=self.asset_manager,
            area=area,
            draw_background=True,
        )

        self.pacman = Pacman(maze=self.maze)
        self.ghosts: list[Ghost] = self._create_ghosts()

        self.collectibles = Collectibles(
            maze=self.maze,
            player_spawn=(
                round(self.pacman.x),
                round(self.pacman.y),
            ),
        )

        self.score = 0
        self.score_font = pygame.font.Font(None, 26)

        self.entity_renderer = EntityRenderer(
            surface=self.surface,
            asset_manager=self.asset_manager,
        )

    def _create_ghosts(self) -> list[Ghost]:
        """Assign each ghost a distinct floor tile near its corner.

        Returns:
            Red, pink, blue and yellow ghosts.

        Raises:
            ValueError: If fewer than four open tiles are available.
        """
        colors: tuple[GhostColor, ...] = (
            "red",
            "pink",
            "blue",
            "yellow",
        )

        corners = (
            (1, 1),
            (self.maze.width - 2, 1),
            (1, self.maze.height - 2),
            (self.maze.width - 2, self.maze.height - 2),
        )

        available = set(self.maze.floors())

        if len(available) < len(colors):
            raise ValueError(
                "The maze needs four open tiles for ghosts."
            )

        ghosts: list[Ghost] = []

        for color, corner in zip(colors, corners):
            cx, cy = corner

            spawn = min(
                available,
                key=lambda tile: (
                    abs(tile[0] - cx) + abs(tile[1] - cy),
                    tile[1],
                    tile[0],
                ),
            )

            available.remove(spawn)

            ghosts.append(
                Ghost(
                    maze=self.maze,
                    color=color,
                    spawn=spawn,
                    speed=4.0,
                )
            )

        return ghosts

    def handle_event(self, event: pygame.event.Event) -> None:
        """Forward player input while the game is active."""
        if not self.game_over and self._hit_pause_remaining == 0:
            self.pacman.handle_event(event)

    def update(self, dt: float) -> None:
        """Advance movement, collisions, collectibles and the timer."""
        if not math.isfinite(dt) or dt <= 0:
            return

        if self.won:
            self._notify_game_win()
            return

        if self.game_over:
            self._notify_game_over()
            return

        if self._hit_pause_remaining > 0:
            self._hit_pause_remaining = max(
                0.0,
                self._hit_pause_remaining - dt,
            )

            if self._hit_pause_remaining == 0:
                self._reset_actors()

            return

        # Collect first so a power gum protects Pac-Man on contact.
        self._collect_pellets()

        if self._check_level_complete():
            return

        if self._check_ghost_contacts():
            return

        remaining = min(dt, self.remaining_time)

        while remaining > 0:
            fastest = max(
                self.pacman.speed,
                max(
                    (ghost.speed * 1.75 for ghost in self.ghosts),
                    default=0.0,
                ),
            )

            # Limit travel between contact checks for fast actors.
            step = min(
                remaining,
                self.UPDATE_STEP,
                0.25 / fastest,
            )

            self.remaining_time = max(
                0.0,
                self.remaining_time - step,
            )

            self._immunity_remaining = max(
                0.0,
                self._immunity_remaining - step,
            )

            self.pacman.update(step)
            self._collect_pellets()

            if self._check_level_complete():
                return

            if self._check_ghost_contacts():
                return

            for ghost in self.ghosts:
                ghost.update(step, self.pacman)

            if self._check_ghost_contacts():
                return

            remaining -= step

        if self.remaining_time <= 0:
            self.game_over = True
            self._notify_game_over()

    def render(self) -> None:
        """Draw the maze, actors, score, lives and remaining time."""
        self.surface.fill((4, 8, 20))

        self.maze_renderer.render()

        self.entity_renderer.render_collectibles(
            collectibles=self.collectibles,
            maze_renderer=self.maze_renderer,
            theme_name=self.theme_manager.current.name,
        )

        for ghost in self.ghosts:
            self.entity_renderer.render_ghost(
                ghost=ghost,
                maze_renderer=self.maze_renderer,
            )

        self.entity_renderer.render_pacman(
            pacman=self.pacman,
            maze_renderer=self.maze_renderer,
        )

        score_image = self.score_font.render(
            f"SCORE  {self.score}",
            True,
            (255, 245, 185),
        )
        self.surface.blit(
            score_image,
            (self.MAZE_MARGIN, 5),
        )

        time_left = max(0, math.ceil(self.remaining_time))
        timer = self.score_font.render(
            f"TIME  {time_left // 60:02}:{time_left % 60:02}",
            True,
            (235, 245, 255),
        )
        self.surface.blit(
            timer,
            timer.get_rect(
                midtop=(self.surface.get_width() // 2, 5),
            ),
        )

        lives_image = self.score_font.render(
            f"LIVES  {self.lives}",
            True,
            (255, 245, 185),
        )
        self.surface.blit(
            lives_image,
            lives_image.get_rect(
                topright=(
                    self.surface.get_width() - self.MAZE_MARGIN,
                    5,
                ),
            ),
        )

        if self.won:
            self._draw_notice("YOU WIN!")
        elif self.game_over or self._hit_pause_remaining > 0:
            message = "GAME OVER" if self.game_over else "LIFE LOST"
            self._draw_notice(message)

    def _draw_notice(self, message: str) -> None:
        """Show a centered message during a hit or completed run."""
        accent = (
            (130, 230, 255)
            if self.theme_manager.current.name == "ice"
            else (215, 150, 255)
        )

        text = self.score_font.render(
            message,
            True,
            accent,
        )
        rect = text.get_rect(
            center=self.surface.get_rect().center,
        )
        panel = rect.inflate(40, 24)

        pygame.draw.rect(
            self.surface,
            (5, 10, 28),
            panel,
            border_radius=10,
        )
        pygame.draw.rect(
            self.surface,
            accent,
            panel,
            width=2,
            border_radius=10,
        )

        self.surface.blit(text, rect)

    def _check_ghost_contacts(self) -> bool:
        """Handle edible ghosts or stop the frame after a harmful hit."""
        self._eat_frightened_ghosts()

        if self._immunity_remaining > 0:
            return False

        for ghost in self.ghosts:
            if not ghost.dangerous:
                continue

            dx = ghost.x - self.pacman.x
            dy = ghost.y - self.pacman.y

            if dx * dx + dy * dy <= self.HIT_DISTANCE ** 2:
                self.lives -= 1

                if self.lives == 0:
                    self.game_over = True
                    self._notify_game_over()
                else:
                    self._hit_pause_remaining = self.HIT_PAUSE

                return True

        return False

    def _reset_actors(self) -> None:
        """Reset actors after a hit while preserving score and pellets."""
        self.pacman = Pacman(
            maze=self.maze,
            speed=self.pacman.speed,
        )

        for ghost in self.ghosts:
            ghost.reset()

        self._immunity_remaining = self.RESPAWN_IMMUNITY

    def _notify_game_over(self) -> None:
        """Send the losing score once through the registered callback."""
        if (
            self.won
            or self._game_over_notified
            or self.on_game_over is None
        ):
            return

        self._game_over_notified = True
        self.on_game_over(self.score)

    def _check_level_complete(self) -> bool:
        """Win this maze after collecting every normal and power gum."""
        if self.collectibles.remaining != 0:
            return False

        self.won = True
        self.game_over = True
        self._notify_game_win()
        return True

    def _notify_game_win(self) -> None:
        """Send the winning score once without opening Game Over."""
        if self._game_win_notified or self.on_game_win is None:
            return

        self._game_win_notified = True
        self.on_game_win(self.score)

    def _collect_pellets(self) -> None:
        """Award collectible points and activate frightened ghost mode."""
        for pellet in self.collectibles.collect_at(
            self.pacman.x,
            self.pacman.y,
        ):
            self.score += pellet.points

            if isinstance(pellet, PowerCrystal):
                for ghost in self.ghosts:
                    ghost.frighten(pellet.duration)

    def _eat_frightened_ghosts(self) -> None:
        """Award points for edible ghosts and send them home."""
        distance_sq = self.GHOST_EAT_DISTANCE ** 2

        for ghost in self.ghosts:
            if not ghost.edible:
                continue

            dx = ghost.x - self.pacman.x
            dy = ghost.y - self.pacman.y

            if dx * dx + dy * dy <= distance_sq and ghost.eat():
                self.score += self.POINTS_PER_GHOST
