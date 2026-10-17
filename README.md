*This activity has been created as part of the 42 curriculum by sabu-kha, aalshoub.*

# Pac-Man

## Description

Pac-Man is a Python arcade game developed as part of the 42 curriculum. The
player explores a generated maze, collects Pacgums, avoids ghosts and uses
Super-pacgums to make ghosts temporarily edible. The project uses an
object-oriented structure, Pygame Community Edition and Ice/Cosmic visual themes.

This document describes the uploaded repository, rather than earlier development
versions. Its active entry point currently runs one fixed 15 × 15 maze. Winning
means collecting every normal and power pellet; losing means exhausting the
three lives or the 90-second timer. Both result screens display the final score.

## Instructions

### Requirements and installation

The subject requires Python 3.10 or later. This source uses Pygame Community
Edition, imported as `pygame`. A graphical desktop and the included image assets
are required. No compilation step is needed for the Python source.

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install pygame-ce
```

On Windows PowerShell, activate the environment using:

```powershell
.\.venv\Scripts\Activate.ps1
```

The archive includes a local `mazegenerator/` directory, so the current source
imports the generator directly. No generator wheel, dependency manifest or
package metadata is included. The assigned external generator must remain
unchanged and must remain compatible when reviewers reinstall it.

### Execution

Launch from the repository root so relative image and data paths resolve:

```bash
python main.py
```

`main.py` creates a 1200 × 800 window and targets 60 frames per second.
`pac-man.py` is empty in this archive and is not a working entry point.

The subject requires exactly one JSON configuration argument, for example
`python3 main.py config.json`. The uploaded `main.py` does not parse command-line
arguments or load that file; supplying an argument does not enable it.

### Controls

| Action | Control |
| --- | --- |
| Move | Arrow keys or W/A/S/D |
| Toggle fullscreen | F11 |
| Play Again on result screens | Enter or Play Again button |
| Return to menu from result screens | Escape or Main Menu button |
| Exit | Quit Game button or close the window |

The Settings screen selects Ice/Cosmic, stores music and sound-effect preferences,
and changes fullscreen/windowed mode. Saving applies the selected theme and
screen mode. Stored sound preferences do not by themselves establish audio playback.

The uploaded active gameplay screen has no pause or cheat shortcuts.

### Development checks

Install the development tools separately:

```bash
python -m pip install flake8 mypy pytest
```

The subject's required lint commands are:

```bash
flake8 .
mypy . --warn-return-any --warn-unused-ignores \
    --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
```

Optional stricter checking:

```bash
mypy . --strict
```

Tests are located in `tests/`, with additional scripts `test_maze.py` and
`test_play.py`. Some tests use older interfaces/imports; their presence is not a
passing test result. A Makefile with `install`, `run`, `debug`, `clean` and `lint`
targets is required by the subject but is absent from this archive.

## Configuration

### Active gameplay values

The current entry point uses these values directly in code:

| Setting | Active value | Source |
| --- | --- | --- |
| Maze size | 15 × 15 generator cells | `main.py` |
| Generator seed | 42 | `main.py` |
| Perfect maze | False | `main.py` |
| Starting lives | 3 | `main.py` |
| Level time | 90 seconds | `main.py` |
| Normal Pacgum points | 10 | `Collectibles` default |
| Super-pacgum points | 50 | `Collectibles` default |
| Edible ghost points | 200 | `GameplayScreen.POINTS_PER_GHOST` |
| Pac-Man speed | 5 tiles/second | `Pacman` default |
| Normal ghost speed | 4 tiles/second | `GameplayScreen._create_ghosts` |

Without an explicit pellet limit, Collectibles fills reachable floor tiles,
excluding the player spawn and the four reserved power-pellet positions.

### Game configuration modules

`config.json` contains a JSON object with a `level` array. Each level contains
integer `width` and `height` values, measured in generator cells. The separate
validator defines these defaults:

| Canonical key | Validator default | Purpose |
| --- | --- | --- |
| `highscore_filename` | `"highscore.json"` | Intended score-file setting |
| `theme` | `"cosmic"` | Intended game theme |
| `lives` | `3` | Starting lives |
| `pacgum` | `42` | Requested normal-pellet count |
| `point_per_pacgum` | `10` | Points per normal pellet |
| `point_per_super_pacgum` | `50` | Points per power pellet |
| `point_per_ghost` | `200` | Points per edible ghost |
| `seed` | `42` | Generator seed |
| `level_max_time` | `90` | Time limit in seconds |
| `level` | Ten square levels | Ordered maze dimensions |

The validator's default square sizes are 14, 18, 22, 26, 30, 34, 38, 42, 46 and
50. The actual supplied config starts with 20 × 20 and uses seed 4. These values
do not control the active main/gameplay path.

The file also uses the misspelled `highscor_filename`, while the validator expects
`highscore_filename`; this validator does not implement a legacy-name alias.
Its point keys intentionally use singular `point_per_...`; subject key names are
indicative, so the spelling must match the implementation.

The loader currently calls `json.load` directly: it does not support hash-comment
lines and does not catch file/JSON errors. The validator supplies defaults for
many invalid fields, but its return is nested under the valid `level_max_time`
branch; an empty config currently returns `None`. These modules need correction
and connection to the entry point to meet the subject's configuration rules.

### Saved user settings

`src/managers/settings_manager.py` uses `data/settings.json`:

| Key | Fallback default | Meaning |
| --- | --- | --- |
| `world` | `"ice"` | Ice or Cosmic theme |
| `music` | `true` | Stored music preference |
| `sfx` | `true` | Stored sound-effect preference |
| `fullscreen` | `true` | Startup display mode |

The checked-in settings instead have Ice selected and music, SFX and fullscreen
set to false. Loading merges valid saved values with defaults. Missing or invalid
settings files fall back to defaults. Saving creates `data/` if necessary.

## Highscore

`src/managers/score_manager.py` stores scores in **`high_scor.json`**, relative to
the current working directory. It does not use `config.json` to select the path.
The archive also contains `data/high_scores.json`, but the score manager does
not read that file.

The storage schema is a JSON list of objects:

```json
[
  {"name": "PLAYER1", "score": 2500},
  {"name": "PLAYER2", "score": 1800}
]
```

The module exposes:

- `load_scores()`: returns an empty list for a missing file, invalid JSON,
  read errors or a non-list document; filters entries by basic name/score types,
  sorts descending by score and returns at most ten entries.
- `save_scores(scores)`: writes the supplied list as formatted JSON.
- `is_high_score(score)`: checks whether there is a free slot or the score exceeds
  the lowest retained score.
- `add_score(name, score)`: loads entries, adds the new result, sorts, retains the
  top ten and saves the list.

JSON suits this small leaderboard because it is readable and needs no database
server. The High Scores screen reloads the score file when entered and displays
saved names and scores.

The current Game Over and Victory screens do **not** collect names or call
`add_score`. The score manager also does not enforce the ten-character limit,
alphanumeric/space restriction or non-negative scores, and write errors are not
caught. These are outstanding requirements, not implemented validation features.
Highscores are loaded on entering their screen rather than at application startup.

## Maze Generation

The active generator integration is:

```python
from mazegenerator.mazegenerator import MazeGenerator

from src.maze.maze import Maze


def create_first_maze() -> Maze:
    """Generate and adapt the initial maze."""
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
```

The generator returns a grid of wall-bit cells: north = 1, east = 2, south = 4
and west = 8. `Maze` adapts the cells into floor/wall tiles. A W × H cell maze
becomes `(2W + 1)` × `(2H + 1)` tiles in the expanded model. Reserved solid cells
form the central 42.

`perfect=False` permits loops and alternative routes. The package must be used
as assigned; the game-side adapter must accommodate its API. The archive alone
does not establish whether its bundled copy is identical to the assigned wheel.

Generator exceptions are wrapped with a readable RuntimeError, but `main()` does
not catch that RuntimeError before exit. Consequently the current failure path
can still produce a traceback and needs a top-level error handler.

A separate `src/systems/level.py` contains an older level model using config
sizes and `seed + level_number - 1`. It is not called by the active
`GameplayScreen`; it does not provide the required random later-level generation
in the current game.

## Implementation

### Game loop and movement

The main loop processes events, updates the active screen using elapsed seconds,
renders it and flips the display. A `finally` block calls `pygame.quit()`.

Pac-Man buffers direction requests and moves between open tile centers. Ghosts
make autonomous movement decisions using `GhostAI`. The gameplay screen checks
contacts before and after movement, using small time slices bounded by actor
speed to reduce missed collisions.

### Collectibles, score and lives

Normal pellets and four power pellets are placed on reachable floor positions.
Power pellets activate frightened mode. Eating an edible ghost awards 200 points;
it returns home before revival. Score increases and is not deducted on a hit.

A harmful ghost contact removes one life. If lives remain, a 1.5-second pause is
followed by actor reset and one second of respawn immunity. Score and collected
pellets remain unchanged. With no lives remaining, Game Over receives the score.

### Timer and outcomes

The 90-second timer advances during active gameplay. Expiry opens Game Over.
Collecting all normal and power pellets opens Victory. Outcome callbacks are
protected against duplicate notification. Play Again constructs a fresh maze
and gameplay instance; result screens also offer Main Menu and Quit.

The HUD displays score, remaining lives and time. It does not display a level
number. There is no active multi-level progression, pause menu or review cheat
mode in this uploaded gameplay screen. `src/screens/pause_screen.py` is empty.

## General Software Architecture

| Component | Responsibility and relationships |
| --- | --- |
| `main.py` | Initializes Pygame/managers and supplies factories and result callbacks |
| `ScreenManager` | Creates registered screens and forwards lifecycle entry hooks |
| `BaseScreen` | Common event, update and render interface |
| `GameplayScreen` | Coordinates Maze, Pacman, Ghost, Collectibles and renderers |
| `src/entities/` | Player movement, ghost state and pellet models |
| `src/systems/collectibles.py` | Placement and one-time collection of pellets |
| `src/systems/ghost_ai.py` | Ghost direction/target decisions |
| `src/maze/` | Generator adaptation and wall/floor queries |
| `MazeRenderer` | Maze drawing and tile-to-window geometry |
| `EntityRenderer` | Actor and collectible drawing using maze geometry |
| `AssetManager` | Shared image loading, transformation and caching |
| `ThemeManager` | Active Ice/Cosmic theme selection |
| `settings_manager.py` | Saved user preferences |
| `score_manager.py` | Standalone persistent Top 10 operations |
| Result screens | Final-score display and navigation |

Gameplay holds model state. Renderers read that state using a shared tile size
and origin. Result callbacks keep gameplay independent of concrete result-screen
classes. `src/core/`, `src/game.py`, `old_code/` and the older Level implementation
are not the screen-based execution path selected by `main.py`.

Current flow:

**Main Menu → Gameplay → Victory or Game Over → Play Again / Main Menu / Quit**

The subject additionally requires name entry and saving after both outcomes.

## Project Management

### Ahmed Alshoubaki — aalshoub

Ahmed's assigned responsibilities cover core gameplay: Pac-Man movement, ghost
AI and behaviour, collision detection, scoring, lives management, level
progression and integration with the assigned MazeGenerator package. He is
responsible for combining the game components into a reliable gameplay system.

### Sadeen — sabu-kha

Sadeen's assigned responsibilities cover screens, navigation, UI components,
asset management and maze/actor rendering. Her work includes Main Menu,
Instructions, Settings, High Scores, Gameplay, Pause and Game Over interfaces,
along with the Ice and Cosmic visual themes.

The uploaded repository contains these planning/design locations:

- [plan/](plan/), including [struct_file.txt](plan/struct_file.txt).
- [flowcharts/](flowcharts/), including the screen-role diagram
  [sadeens_role.jpeg](flowcharts/sadeens_role.jpeg).

The subject also calls for evidence of scheduling/progress, technical choices,
risks, team decisions and acceptance testing. A separate `project_management/`
documentation package was prepared during development, but it is not present in
this uploaded archive and must be included if used for the submission.

## Packaging and Submission Status

`packaging/package.sh` exists but is empty. No root packaging script/spec,
Makefile, dependency manifest or generator wheel is included. The archive does
not provide a reproducible packaging command or a distribution URL. An Itch.io
upload was reported during development, but its downloadable build was not
provided for verification.

The subject requires a working free unlisted/private platform build, minimal
in-package instructions, complete source and a packaging script/spec at the
repository root, with the ability to rebuild during review.

The following requirements remain unfulfilled in the active uploaded code:

1. Exactly one JSON argument, commented-JSON support and robust config integration.
2. At least ten connected levels, random later mazes and retained score/lives.
3. Pause/resume, a useful review cheat mode and the current-level HUD field.
4. Name entry after both outcomes, complete score validation and automatic saving.
5. Required Makefile targets and functional reproducible packaging.

The required MLX-equivalence restriction on graphical functions also needs a
separate API review. Having this README does not certify those game requirements.

## Resources

- Pac-Man subject, version 1.5, supplied by 42.
- The assigned A-Maze-ing package and its original API documentation.
- [Python documentation](https://docs.python.org/3/).
- [Python virtual environments](https://docs.python.org/3/library/venv.html).
- [Pygame Community Edition documentation](https://pyga.me/docs/).
- [Flake8 documentation](https://flake8.pycqa.org/en/latest/).
- [mypy documentation](https://mypy.readthedocs.io/en/stable/).

### Use of AI

ChatGPT assisted with explanations and debugging, maze integration and rendering,
entity movement, screen management and outcome callbacks, visual asset ideas and
generation, README drafting and project-management records. Generated code and
suggestions were provided for these areas during development.

The contributors remain responsible for reviewing and understanding retained
code, testing it against the assigned package and seeking peer review. During
this documentation review, Python syntax was checked without errors across the
archive; isolated checks confirmed score sorting, malformed-score-file recovery,
the validator's empty-config issue and the loader's rejection of hash comments.
No graphical gameplay run, full lint/type-check pass or packaged-build test is
claimed by this README.
