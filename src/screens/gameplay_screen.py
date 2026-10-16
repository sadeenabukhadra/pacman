"""Display the maze and control Pac-Man during gameplay."""

import math

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
    """Coordinate maze drawing, player input, movement and animation.

    Pacman owns player state and movement. EntityRenderer owns sprite
    loading and drawing. MazeRenderer supplies their shared coordinates.
    """

    MAZE_MARGIN = 30
    POINTS_PER_GHOST = 200
    UPDATE_STEP = 1.0 / 120.0
    GHOST_EAT_DISTANCE = 0.55

    def __init__(
        self,
        surface: pygame.Surface,
        maze: Maze,
        theme_manager: ThemeManager,
        asset_manager: AssetManager,
    ) -> None:
        """Create the maze renderer, player and player renderer.

        Args:
            surface: Display surface used by the game loop.
            maze: Playable maze shared by drawing and movement.
            theme_manager: Manager providing the selected theme.
            asset_manager: Shared image cache.
        """
        super().__init__(surface)
        self.maze = maze
        self.theme_manager = theme_manager
        self.asset_manager = asset_manager

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
            player_spawn=(round(self.pacman.x), round(self.pacman.y)),
        )
        self.score = 0
        self.score_font = pygame.font.Font(None, 26)
        self.entity_renderer = EntityRenderer(
            surface=self.surface,
            asset_manager=self.asset_manager,
        )

    def _create_ghosts(self) -> list[Ghost]:
        """Assign each personality a distinct open tile near its corner.

        Returns:
            Red, pink, blue and yellow ghosts in corner order.

        Raises:
            ValueError: If fewer than four open tiles are available.
        """
        colors: tuple[GhostColor, ...] = ("red", "pink", "blue", "yellow")
        corners = (
            (1, 1),
            (self.maze.width - 2, 1),
            (1, self.maze.height - 2),
            (self.maze.width - 2, self.maze.height - 2),
        )
        available = set(self.maze.floors())
        if len(available) < len(colors):
            raise ValueError("The maze needs four open tiles for ghosts.")
        ghosts: list[Ghost] = []
        for color, corner in zip(colors, corners):
            cx, cy = corner
            spawn = min(
                available,
                key=lambda tile: (
                    abs(tile[0] - cx) + abs(tile[1] - cy),
                    tile[1], tile[0],
                ),
            )
            available.remove(spawn)
            ghosts.append(Ghost(
                maze=self.maze,
                color=color,
                spawn=spawn,
                speed=4.0,
            ))
        return ghosts

    def handle_event(self, event: pygame.event.Event) -> None:
        """Forward keyboard input to the player.

        Args:
            event: Event received from the main game loop.
        """
        self.pacman.handle_event(event)

    def update(self, dt: float) -> None:
        """Advance player animation and each ghost's autonomous movement.

        Args:
            dt: Elapsed time in seconds since the previous frame.
        """
        if not math.isfinite(dt) or dt <= 0:
            return
        # Collect before moving too, covering pellets already under the player.
        self._collect_pellets()
        remaining = dt
        while remaining > 0:
            step = min(remaining, self.UPDATE_STEP)
            self.pacman.update(step)
            self._collect_pellets()
            for ghost in self.ghosts:
                ghost.update(step, self.pacman)
            self._eat_frightened_ghosts()
            remaining -= step

    def render(self) -> None:
        """Draw the maze, ghosts and player in their shared tile coordinates."""
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
            f"SCORE  {self.score}", True, (255, 245, 185),
        )
        self.surface.blit(score_image, (self.MAZE_MARGIN, 5))

    def _collect_pellets(self) -> None:
        """Award points once and apply power effects to all active ghosts."""
        for pellet in self.collectibles.collect_at(
            self.pacman.x, self.pacman.y,
        ):
            self.score += pellet.points
            if isinstance(pellet, PowerCrystal):
                for ghost in self.ghosts:
                    ghost.frighten(pellet.duration)

    def _eat_frightened_ghosts(self) -> None:
        """Award ghost points and send edible ghosts back to their corners."""
        distance_sq = self.GHOST_EAT_DISTANCE ** 2
        for ghost in self.ghosts:
            if not ghost.edible:
                continue
            dx = ghost.x - self.pacman.x
            dy = ghost.y - self.pacman.y
            if dx * dx + dy * dy <= distance_sq and ghost.eat():
                self.score += self.POINTS_PER_GHOST