"""Preview only the maze: Escape exits and Space changes the theme."""

import pygame

from mazegenerator.mazegenerator import MazeGenerator
from src.managers.asset_manager import AssetManager
from src.maze.maze import Maze
from src.rendering.maze_renderer import MazeRenderer
from src.themes.theme_manager import ThemeManager


# Keep the uploaded generator settings to preserve the current layout.
WIDTH, HEIGHT = 24, 24


def main() -> None:
    """Create the original maze and show the connected-wall renderer."""
    pygame.init()
    try:
        surface = pygame.display.set_mode((1200, 800))
        pygame.display.set_caption("Pac-Man | Maze preview")
        try:
            generator = MazeGenerator(
                size=(WIDTH, HEIGHT), perfect=False, seed=42,
            )
            maze = Maze(generator.maze)
        except Exception as error:
            raise RuntimeError(f"Cannot create the maze: {error}") from error

        themes = ThemeManager("cosmic")
        renderer = MazeRenderer(
            surface, maze, themes, AssetManager(),
            area=pygame.Rect(0, 12, 1200, 776),
        )
        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        themes.set_theme(
                            "cosmic" if themes.current.name == "ice"
                            else "ice"
                        )
            renderer.render()
            pygame.display.flip()
            clock.tick(60)
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
