from src.maze.maze_adapter import MazeAdapter


adapter = MazeAdapter(width=14, height=14, seed=42)

assert len(adapter.maze) == 14
assert all(len(row) == 14 for row in adapter.maze)

print("Maze created successfully")
print("Number of rows:", len(adapter.maze))
print("Number of columns:", len(adapter.maze[0]))
print("First row:", adapter.maze[0])