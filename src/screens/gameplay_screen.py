"""Display the maze and control Pac-Man during gameplay."""

import math
from collections.abc import Callable

import pygame

from src.config.config_validater import GameConfig
from src.entities.ghost import Ghost
from src.entities.pacman import Pacman
from src.entities.power_crystal import PowerCrystal
from src.managers.asset_manager import AssetManager
from src.managers.display_manager import DisplayManager
from src.maze.maze import Maze
from src.rendering.entity_renderer import EntityRenderer
from src.rendering.maze_renderer import MazeRenderer
from src.screens.base_screen import BaseScreen
from src.screens.pause_screen import PauseScreen
from src.systems.cheats import CheatMode
from src.systems.collectibles import Collectibles
from src.systems.display_layout import DisplayPlan
from src.systems.ghost_ai import GhostColor
from src.systems.level_progression import LevelProgression
from src.themes.theme_manager import ThemeManager
from src.ui.cheat_panel import CheatPanel
from src.ui.countdown import Countdown
from src.ui.game_notice import GameNotice
from src.ui.hud import HUD


class GameplayScreen(BaseScreen):
    """Coordinate maze drawing, player input, movement and animation.

    Pacman owns player state and movement. EntityRenderer owns sprite
    loading and drawing. MazeRenderer supplies their shared coordinates.
    """

    MAZE_MARGIN = 4
    HIT_PAUSE = 1.8
    RESPAWN_IMMUNITY = 1.0
    HIT_DISTANCE = 0.60
    UPDATE_STEP = 1.0 / 120.0
    GHOST_EAT_DISTANCE = 0.55
    BASE_GHOST_SPEED = 4.0
    GHOST_SPEED_INCREMENT = 1.0
    MAX_MOVEMENT_PER_STEP = 0.25

    def __init__(
        self,
        surface: pygame.Surface,
        maze: Maze,
        theme_manager: ThemeManager,
        asset_manager: AssetManager,
        config: GameConfig,
        on_main_menu: Callable[[], None],
        on_restart: Callable[[], None],
        on_game_over: Callable[[int], None] | None = None,
        display_manager: DisplayManager | None = None,
        entity_renderer: EntityRenderer | None = None,
    ) -> None:
        """Create the maze renderer, player and player renderer.

        Args:
            surface: Display surface used by the game loop.
            maze: Playable maze shared by drawing and movement.
            theme_manager: Manager providing the selected theme.
            asset_manager: Shared image cache.
            config: Validated game settings received from main.
            on_main_menu: Callback that returns to the registered main menu.
            on_restart: Callback that creates a fresh gameplay screen.
            on_game_over: Optional callback receiving the final score.
            entity_renderer: Optional preloaded shared sprite renderer.
        """
        super().__init__(surface)
        self.maze = maze
        self.theme_manager = theme_manager
        self.asset_manager = asset_manager
        self.config = config
        self.display_manager = display_manager
        self.screen_limit: DisplayPlan | None = None
        self.on_game_over = on_game_over
        self.on_main_menu = on_main_menu
        self.on_restart = on_restart
        self.pause_screen: PauseScreen | None = None
        self._pause_icons: dict[str, pygame.Surface] = {}
        self.lives = config["lives"]
        self.points_per_ghost = config["point_per_ghost"]
        self.game_over = False
        self.won = False
        self.level_error = ""
        self._game_over_notified = False
        self._hit_pause_remaining = 0.0
        self._immunity_remaining = 0.0

        self.level = 1
        self.remaining_time = float(config["level_max_time"])
        self.timed_out = False
        self.hud = HUD(
            surface=self.surface,
            asset_manager=self.asset_manager,
            theme_manager=self.theme_manager,
        )
        self.levels = LevelProgression(config)
        self.cheats = CheatMode()
        self.cheat_panel = CheatPanel(self.surface)
        self._build_level(maze, config["seed"])
        self.score = 0
        self.entity_renderer = (
            entity_renderer if entity_renderer is not None else EntityRenderer(
                surface=self.surface,
                asset_manager=self.asset_manager,
            )
        )
        self.entity_renderer.surface = self.surface

    def _build_level(
        self, maze: Maze, seed: int, level_number: int = 1,
    ) -> None:
        """Prepare all level objects before replacing the current ones."""
        pacman = Pacman(maze=maze)
        normal_speed = pacman.speed
        pacman.speed = normal_speed * self.cheats.speed_multiplier
        ghosts = self._create_ghosts(maze, level_number)
        collectibles = Collectibles(
            maze=maze,
            player_spawn=(round(pacman.x), round(pacman.y)),
            pacgum_count=None,  # Fill every reachable corridor tile.
            points_per_pacgum=self.config["point_per_pacgum"],
            points_per_super_pacgum=self.config["point_per_super_pacgum"],
            seed=seed,
        )
        renderer, countdown, notice, plan = self._prepare_view(maze)
        self.maze = maze
        self.maze_renderer = renderer
        self.countdown = countdown
        self.game_notice = notice
        self.screen_limit = plan if plan is not None and plan.limited else None
        self.pacman = pacman
        self._normal_player_speed = normal_speed
        self.ghosts = ghosts
        self.collectibles = collectibles
        self.remaining_time = float(self.config["level_max_time"])
        self._hit_pause_remaining = 0.0
        self._immunity_remaining = 0.0
        self.timed_out = False

    def _prepare_view(
        self, maze: Maze,
    ) -> tuple[MazeRenderer, Countdown, GameNotice, DisplayPlan | None]:
        """Grow the window within desktop limits and fit the complete maze."""
        preferred = getattr(
            self,
            "_view_tile_size",
            max(
                16,
                min(
                    24,
                    (
                        self.surface.get_width()
                        - 2 * self.MAZE_MARGIN
                    ) // maze.width,
                    (
                        self.surface.get_height()
                        - self.hud.height
                        - 2 * self.MAZE_MARGIN
                    ) // maze.height,
                ),
            ),
        )
        plan = None
        if self.display_manager is not None:
            plan = self.display_manager.prepare_maze(
                (maze.width, maze.height), preferred, self.hud.height,
                self.MAZE_MARGIN,
            )
            self.surface = self.display_manager.surface
            self._bind_surface(self.surface)
        # Reserve the full HUD strip above the maze, plus outer margins.
        area = pygame.Rect(
            self.MAZE_MARGIN,
            self.hud.height + self.MAZE_MARGIN,
            self.surface.get_width() - 2 * self.MAZE_MARGIN,
            self.surface.get_height() - self.hud.height
            - 2 * self.MAZE_MARGIN,
        )
        tile_size = plan.tile_size if plan is not None else min(
            preferred, area.width // maze.width, area.height // maze.height,
        )
        renderer = MazeRenderer(
            surface=self.surface,
            maze=maze,
            theme_manager=self.theme_manager,
            asset_manager=self.asset_manager,
            area=area,
            draw_background=True,
            tile_size=tile_size,
        )
        countdown = Countdown(
            surface=self.surface,
            area=renderer.visible_rect(),
        )
        notice = GameNotice(self.surface, countdown.area)
        self._view_tile_size = preferred
        return renderer, countdown, notice, plan

    def _bind_surface(self, surface: pygame.Surface) -> None:
        """Rebind every drawable after a native display mode change."""
        self.surface = surface
        for name in (
            "hud", "cheat_panel", "entity_renderer", "maze_renderer",
            "countdown", "game_notice",
        ):
            drawable = getattr(self, name, None)
            if drawable is not None:
                drawable.surface = surface

    def relayout(self) -> None:
        """Refresh fullscreen/window layout without resetting the run."""
        elapsed = self.countdown.elapsed
        renderer, countdown, notice, plan = self._prepare_view(self.maze)
        self.maze_renderer, self.countdown, self.game_notice = (
            renderer, countdown, notice,
        )
        self.countdown.elapsed = elapsed
        self.screen_limit = plan if plan is not None and plan.limited else None
        self._pause_icons.clear()
        if self.pause_screen is not None:
            self.pause_screen = None
            self._open_pause()

    def _create_ghosts(self, maze: Maze, level_number: int) -> list[Ghost]:
        """Assign each personality a distinct open tile near its corner.

        Returns:
            Red, pink, blue and yellow ghosts in corner order.

        Raises:
            ValueError: If fewer than four open tiles are available.
        """
        speed = (
            self.BASE_GHOST_SPEED
            + self.GHOST_SPEED_INCREMENT * (level_number - 1)
        )
        colors: tuple[GhostColor, ...] = ("red", "pink", "blue", "yellow")
        corners = (
            (1, 1),
            (maze.width - 2, 1),
            (1, maze.height - 2),
            (maze.width - 2, maze.height - 2),
        )
        available = set(maze.floors())
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
                maze=maze,
                color=color,
                spawn=spawn,
                speed=speed,
            ))
        return ghosts

    def _advance_level(self) -> None:
        """Complete one level, preserving score, lives and review toggles."""
        if self.game_over or self._hit_pause_remaining > 0:
            return
        if self.levels.is_last:
            self.won = True
            self.game_over = True
            self._notify_game_over()
            return
        previous_size = self.surface.get_size()
        try:
            maze, seed = self.levels.prepare_next()
            self._build_level(maze, seed, self.level + 1)
        except Exception as error:
            if self.display_manager is not None:
                self.display_manager.restore_size(previous_size)
                self._bind_surface(self.display_manager.surface)
            self.level_error = "NEXT LEVEL COULD NOT BE LOADED"
            print(f"Warning: level {self.level + 1} could not load: {error}")
            return
        self.levels.commit_next(seed)
        self.level = self.levels.index + 1
        self.level_error = ""

    def _check_level_complete(self) -> bool:
        """Stop this frame when no normal or power pellets remain."""
        if self.collectibles.remaining != 0:
            return False
        self._advance_level()
        return True

    def handle_event(self, event: pygame.event.Event) -> None:
        """Forward keyboard input to the player.

        Args:
            event: Event received from the main game loop.
        """
        if event.type in (pygame.KEYUP, pygame.WINDOWFOCUSLOST):
            self.cheats.handle_event(event)
        if self.screen_limit is not None:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.screen_limit = None
                elif event.key == pygame.K_ESCAPE:
                    self._return_to_menu()
            return
        if self.pause_screen is not None:
            self.pause_screen.handle_event(event)
            return
        if self.won or self.level_error:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                    self._return_to_menu()
                elif event.key == pygame.K_r:
                    self._restart()
                elif (
                    self.level_error and event.key == pygame.K_n
                    and not getattr(event, "repeat", False)
                ):
                    self._advance_level()
            return
        if self.game_over or self._hit_pause_remaining > 0:
            return
        action = self.cheats.handle_event(event)
        if action is not None:
            if action == "next":
                self._advance_level()
                return
            if action == "life":
                self.lives += 1
            self.pacman.speed = (
                self._normal_player_speed * self.cheats.speed_multiplier
            )
            return
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_p):
                self._open_pause()
                return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._pause_button_rect().collidepoint(event.pos):
                self._open_pause()
                return
        if not self.countdown.active:
            self.pacman.handle_event(event)

    def update(self, dt: float) -> None:
        """Advance player animation and each ghost's autonomous movement.

        Args:
            dt: Elapsed time in seconds since the previous frame.
        """
        if not math.isfinite(dt) or dt <= 0:
            return
        if self.pause_screen is not None:
            return
        if self.won:
            self._notify_game_over()
            return
        if self.level_error or self.screen_limit is not None:
            return
        if self.countdown.active:
            self.countdown.update(dt)
            return
        if self._hit_pause_remaining > 0:
            self._hit_pause_remaining = max(
                0.0, self._hit_pause_remaining - dt,
            )
            if self._hit_pause_remaining == 0:
                self._finish_hit_pause()
            return
        if self.game_over:
            self._notify_game_over()
            return

        # Collect first so a power pellet can protect the player on contact.
        self._collect_pellets()
        if self._check_level_complete():
            return
        if self._check_ghost_contacts():
            return
        remaining = min(dt, self.remaining_time)
        while remaining > 0:
            step = min(remaining, self._movement_step())
            if not self.cheats.freeze_time:
                self.remaining_time = max(0.0, self.remaining_time - step)
            self._immunity_remaining = max(
                0.0, self._immunity_remaining - step,
            )
            self.pacman.update(step)
            self._collect_pellets()
            if self._check_level_complete():
                return
            if self._check_ghost_contacts():
                return
            if not self.cheats.freeze_ghosts:
                for ghost in self.ghosts:
                    ghost.update(step, self.pacman)
            if self._check_ghost_contacts():
                return
            remaining -= step
        if self.remaining_time <= 0:
            self.timed_out = True
            self.game_over = True
            self._notify_game_over()

    def _movement_step(self) -> float:
        """Keep fast ghosts from crossing a player between contact checks."""
        fastest = self.pacman.speed
        if not self.cheats.freeze_ghosts:
            # Returning eyes can move at 1.75 times the normal ghost speed.
            fastest = max(
                fastest, max((ghost.speed * 1.75 for ghost in self.ghosts),
                             default=0.0),
            )
        return min(self.UPDATE_STEP, self.MAX_MOVEMENT_PER_STEP / fastest)

    def render(self, show_end_notice: bool = True) -> None:
        """Draw the maze, actors, HUD and any active overlay."""
        self.surface.fill((4, 8, 20))
        self.maze_renderer.follow(self.pacman.x, self.pacman.y)
        self.maze_renderer.render()
        previous_clip = self.surface.get_clip()
        self.surface.set_clip(previous_clip.clip(self.maze_renderer.area))
        try:
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
        finally:
            self.surface.set_clip(previous_clip)
        # Draw last: MazeRenderer may repaint the full-window background.
        self.hud.render(
            level=self.level,
            score=self.score,
            remaining_time=self.remaining_time,
            lives=self.lives,
        )
        if (
            not self.game_over and not self.level_error
            and self._hit_pause_remaining == 0
        ):
            self._draw_pause_button()
        self.cheat_panel.render(
            self.cheats, self.countdown.area, self.theme_manager.current.name,
        )
        if self.level_error:
            self.game_notice.render(
                theme_name=self.theme_manager.current.name,
                title="LEVEL ERROR",
                detail=self.level_error,
                footer="N: RETRY   ENTER: MENU   R: RESTART",
            )
        elif self.won and show_end_notice:
            self.game_notice.render(
                theme_name=self.theme_manager.current.name,
                title="YOU WIN!",
                detail=f"FINAL SCORE: {self.score}",
                footer="ENTER: MAIN MENU   R: RESTART",
            )
        elif (
            show_end_notice and not self.game_over
            and self._hit_pause_remaining > 0
        ):
            message = "GAME OVER" if self.game_over else "LIFE LOST"
            detail = (
                "1 LIFE REMAINS" if self.lives == 1
                else f"{self.lives} LIVES REMAIN"
            )
            if self.game_over:
                detail = "NO LIVES REMAIN"
            if self.timed_out:
                message = "TIME UP"
                detail = "THE LEVEL TIMER HAS ENDED"
            progress = None if self.game_over else (
                1.0 - self._hit_pause_remaining / self.HIT_PAUSE
            )
            self.game_notice.render(
                theme_name=self.theme_manager.current.name,
                title=message,
                detail=detail,
                progress=progress,
            )
        if (
            not self.won and not self.level_error
            and self.screen_limit is None
        ):
            self.countdown.render(self.theme_manager.current.name)
        if self.pause_screen is not None:
            self.pause_screen.render()
        if self.screen_limit is not None:
            plan = self.screen_limit
            mode = "FULLSCREEN" if plan.fullscreen else "WINDOWED"
            self.game_notice.render(
                theme_name=self.theme_manager.current.name,
                title="SCREEN LIMIT REACHED",
                detail=(f"Requested {plan.required[0]} x {plan.required[1]}"
                        f" | Limit {plan.available[0]} x {plan.available[1]}"),
                secondary="Maze fitted to screen; the full maze is visible.",
                footer="ENTER / SPACE: CONTINUE   ESC: MENU",
                caption=mode,
            )

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
                self.score += self.points_per_ghost

    def _check_ghost_contacts(self) -> bool:
        """Handle one dangerous hit or edible ghost contacts.

        Returns:
            True if a hit stopped this update. Returning eyes are harmless.
        """
        if self.game_over or self._hit_pause_remaining > 0:
            return True
        if not self.cheats.invincible and self._immunity_remaining == 0:
            for ghost in self.ghosts:
                if not ghost.dangerous:
                    continue
                dx = ghost.x - self.pacman.x
                dy = ghost.y - self.pacman.y
                if dx * dx + dy * dy <= self.HIT_DISTANCE ** 2:
                    self._lose_life()
                    return True
        self._eat_frightened_ghosts()
        return False

    def _lose_life(self) -> None:
        """Deduct exactly one life and begin a non-blocking hit pause."""
        if (
            self.game_over or self._hit_pause_remaining > 0
            or self._immunity_remaining > 0 or self.cheats.invincible
        ):
            return
        self.lives = max(0, self.lives - 1)
        self._hit_pause_remaining = self.HIT_PAUSE
        self.game_over = self.lives == 0
        if self.game_over:
            self._hit_pause_remaining = 0.0
            self._notify_game_over()

    def _finish_hit_pause(self) -> None:
        """End the game or reset only actors, preserving level progress."""
        if self.game_over:
            self._notify_game_over()
            return
        speed = self.pacman.speed
        self.pacman = Pacman(maze=self.maze, speed=speed)
        for ghost in self.ghosts:
            ghost.reset()
        self._immunity_remaining = self.RESPAWN_IMMUNITY

    def _notify_game_over(self) -> None:
        """Send the final score to the screen-switch callback at most once."""
        if self._game_over_notified or self.on_game_over is None:
            return
        self.render(show_end_notice=False)
        self._game_over_notified = True
        self.on_game_over(self.score)

    def _pause_button_rect(self) -> pygame.Rect:
        """Position a clear pause control to the left of the HUD panel."""
        side = max(36, min(
            80, self.hud.height - 24,
            round(self.surface.get_width() * 0.067),
        ))
        rect = pygame.Rect(0, 0, side, side)
        rect.midleft = (12, self.hud.height // 2)
        return rect

    def _draw_pause_button(self) -> None:
        """Separate the supplied pause icon from the bright game background."""
        name = self.theme_manager.current.name
        theme = name if name in ("ice", "cosmic") else "ice"
        rect = self._pause_button_rect()
        color = (130, 225, 255) if theme == "ice" else (215, 145, 255)
        pygame.draw.rect(
            self.surface, (5, 9, 28), rect, border_radius=14,
        )
        pygame.draw.rect(
            self.surface, color, rect, width=2, border_radius=14,
        )
        if theme not in self._pause_icons:
            filename = "pause_ice.png" if theme == "ice" else "puse.png"
            source = self.asset_manager.load(f"maze/{theme}/puse/{filename}")
            bounds = source.get_bounding_rect(min_alpha=48)
            if bounds.width > 0 and bounds.height > 0:
                source = source.subsurface(bounds).copy()
            inner_side = max(1, rect.width - 20)
            factor = min(
                inner_side / source.get_width(),
                inner_side / source.get_height(),
            )
            self._pause_icons[theme] = pygame.transform.smoothscale(source, (
                max(1, round(source.get_width() * factor)),
                max(1, round(source.get_height() * factor)),
            ))
        image = self._pause_icons[theme]
        self.surface.blit(image, image.get_rect(center=rect.center))

    def _open_pause(self) -> None:
        """Create an overlay without replacing the running game instance."""
        if (
            self.pause_screen is not None or self.game_over
            or self._hit_pause_remaining > 0
        ):
            return
        self.pause_screen = PauseScreen(
            surface=self.surface,
            theme_manager=self.theme_manager,
            asset_manager=self.asset_manager,
            on_resume=self._resume,
            on_restart=self._restart,
            on_main_menu=self._return_to_menu,
        )

    def _resume(self) -> None:
        """Close the overlay while preserving every gameplay state value."""
        self.pause_screen = None

    def _return_to_menu(self) -> None:
        """Close the overlay and ask the application to show the main menu."""
        self.pause_screen = None
        self.on_main_menu()

    def _restart(self) -> None:
        """Discard this session through the application's new-game factory."""
        self.pause_screen = None
        self.on_restart()
