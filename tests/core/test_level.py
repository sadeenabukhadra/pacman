import unittest

from src.systems.level import LevelManager


class TestLevelManager(unittest.TestCase):
    def setUp(self) -> None:
        self.config = {
            "seed": 42,
            "level": [
                {"width": 14, "height": 14},
                {"width": 18, "height": 18},
            ],
        }

    def test_start_level_creates_maze_with_configured_size(self) -> None:
        manager = LevelManager(self.config)

        manager.start_level()

        self.assertEqual(len(manager.maze), 14)
        self.assertTrue(all(len(row) == 14 for row in manager.maze))

    def test_next_level_creates_maze_with_next_level_size(self) -> None:
        manager = LevelManager(self.config)
        manager.start_level()

        moved = manager.next_level()

        self.assertTrue(moved)
        self.assertEqual(manager.current_index, 1)
        self.assertEqual(len(manager.maze), 18)
        self.assertTrue(all(len(row) == 18 for row in manager.maze))

if __name__ == "__main__":
    unittest.main()