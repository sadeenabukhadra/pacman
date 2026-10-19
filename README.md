*This activity has been created as part of the 42 curriculum by sabu-kha, aalshoub.*

# Pac-Man

A Python maze arcade game featuring Ice and Cosmic visual themes,
generated levels, autonomous ghosts and persistent highscores.

[Download the Linux build on Itch.io](https://ahm5edt456.itch.io/pacman)

## Table of Contents

- [Description](#description)
- [Instructions](#instructions)
- [Configuration](#configuration)
- [Highscore](#highscore)
- [Maze Generation](#maze-generation)
- [Implementation](#implementation)
- [General Software Architecture](#general-software-architecture)
- [Project Management](#project-management)
- [Packaging and Distribution](#packaging-and-distribution)
- [Validation and Review](#validation-and-review)
- [Troubleshooting](#troubleshooting)
- [Resources](#resources)

## Description

This project recreates the core experience of Pac-Man using Python,
object-oriented programming and Pygame Community Edition.

The player navigates generated corridors, collects Pacgums, avoids
ghosts and uses Super-pacgums to make ghosts temporarily edible.
The game includes configurable levels, scoring, lives, a level timer,
pause handling and final-result screens.

Two visual themes are available:

- **Ice:** blue and cyan environments with icy walls.
- **Cosmic:** dark space environments with purple and blue lighting.

The implementation separates gameplay state, screen navigation,
rendering, configuration and persistence into dedicated modules.

### Main features

- Configurable game parameters through a JSON file.
- Full-line `#` comments in configuration files.
- Independent defaults for missing or invalid configuration fields.
- Integration with the assigned external maze generator.
- Autonomous ghosts with normal, frightened and eaten states.
- Normal pellets and four corner power pellets.
- Score, lives, level and remaining-time displays.
- Pause and resume.
- Review cheat controls.
- Persistent Top 10 leaderboard.
- Name entry after victory or defeat.
- Ice/Cosmic theme selection.
- Fullscreen/windowed settings.
- Reproducible Linux packaging.

## Instructions

### Requirements

For source execution:

- Python 3.10 or later.
- Pygame Community Edition.
- The assigned A-Maze-ing package.
- A graphical desktop.
- The included image assets.

For development:

- Flake8.
- mypy.

For packaging:

- PyInstaller.
- Bash for the supplied build script.

The development environment used for the project includes Python 3.14
and `pygame-ce==2.5.8`. Platform compatibility should be tested using
the final packaged build.

### Install from source

Open a terminal in the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install ./mazegenerator-2.1.0-py3-none-any.whl
```

Pygame Community Edition is installed as `pygame-ce` but imported
in Python as `pygame`.

The assigned maze generator must be installed and used without
modifying its implementation.

To leave the virtual environment:

```bash
deactivate
```

### Launch from source

```bash
python3 pac-man.py config.json
```

The launcher expects exactly one argument: a JSON configuration file.

A different filename can be supplied:

```bash
python3 pac-man.py custom_config.json
```

Run from the repository root so project-relative asset paths resolve.

The Makefile also provides:

```bash
make run
```

### Launch the packaged version

Download the archive from:

https://ahm5edt456.itch.io/pacman

Extract the entire archive into a writable directory and run:

```bash
bash play.sh
```

Alternatively:

```bash
./pac-man config.json
```

Keep the executable and its accompanying assets together.
The packaged version does not require a separate Python installation.

The distributed build targets Linux. It is not a Windows executable
or a browser-playable version.

### Controls

| Action | Control |
| --- | --- |
| Move up | Up arrow or W |
| Move down | Down arrow or S |
| Move left | Left arrow or A |
| Move right | Right arrow or D |
| Navigate Settings | Arrow keys or mouse |
| Activate a Settings item | Enter, Space or mouse click |
| Leave Settings | Escape or Back to Menu |
| Inspect review shortcuts | In-game cheat panel |

Use an English keyboard layout when testing W/A/S/D.

The Instructions screen describes gameplay controls and rules.
The pause menu provides resume and return-to-menu actions.

### Main menu

The main menu provides access to:

- Start Game.
- Instructions.
- High Scores.
- Settings.
- Quit Game.

### Settings

The Settings screen provides:

- Ice/Cosmic theme selection.
- Fullscreen/windowed mode.
- Save Settings.
- Back to Menu.

The current theme is selected when the screen is entered.
Music and sound-effect switches were removed from the interface.

### Makefile commands

| Target | Purpose |
| --- | --- |
| `make install` | Install project dependencies |
| `make run` | Run the game |
| `make debug` | Run using Python's debugger |
| `make clean` | Remove temporary files and caches |
| `make lint` | Run Flake8 and the required mypy checks |

The required checking commands are:

```bash
python3 -m flake8 .
python3 -m mypy . --warn-return-any --warn-unused-ignores \
    --ignore-missing-imports --disallow-untyped-defs \
    --check-untyped-defs
```

Optional stricter type checking:

```bash
python3 -m mypy . --strict
```

Any third-party checking exclusions must be limited to the external
generator. The game's adapter and integration code remain part of
the project's checks.

## Configuration

### Format

The configuration contains a JSON object with game parameters and an
ordered array of levels.

Full-line comments beginning with `#` are supported, including
indented comments:

```text
{
    # Starting visual theme
    "theme": "ice",
    "lives": 3
}
```

This comment support is provided by the project loader; comments are
not part of standard JSON.

### Configuration keys

| Canonical key | Default | Description |
| --- | --- | --- |
| `highscore_filename` | `"highscore.json"` | Score-file location |
| `theme` | `"cosmic"` | Initial Ice/Cosmic theme |
| `lives` | `3` | Initial number of lives |
| `pacgum` | `42` | Normal-pellet count setting |
| `point_per_pacgum` | `10` | Points awarded for a normal pellet |
| `point_per_super_pacgum` | `50` | Points awarded for a power pellet |
| `point_per_ghost` | `200` | Points awarded for an edible ghost |
| `seed` | `42` | Initial generator seed |
| `level_max_time` | `90` | Time allowed per level, in seconds |
| `level` | Ten default levels | Ordered generator dimensions |

Default square maze sizes are:

```text
14, 18, 22, 26, 30, 34, 38, 42, 46, 50
```

These are validator defaults. Values in the supplied `config.json`
override them when valid.

### Complete example

```json
{
  "highscore_filename": "highscore.json",
  "theme": "ice",
  "lives": 3,
  "pacgum": 42,
  "point_per_pacgum": 10,
  "point_per_super_pacgum": 50,
  "point_per_ghost": 200,
  "seed": 42,
  "level_max_time": 90,
  "level": [
    {"width": 14, "height": 14},
    {"width": 18, "height": 18},
    {"width": 22, "height": 22},
    {"width": 26, "height": 26},
    {"width": 30, "height": 30},
    {"width": 34, "height": 34},
    {"width": 38, "height": 38},
    {"width": 42, "height": 42},
    {"width": 46, "height": 46},
    {"width": 50, "height": 50}
  ]
}
```

### Validation rules

- Unknown keys are ignored.
- Missing or invalid fields receive their own default.
- Valid fields remain unchanged.
- Boolean values are not accepted as integer settings.
- Lives, seed and level time must be positive integers.
- Pellet counts and point values must be non-negative integers.
- Maze dimensions must be integers from 3 to 100.
- Short level lists are extended to at least ten entries.
- Invalid dimensions are replaced independently.
- The score filename must be a non-empty string without null characters.

For example, an invalid height does not discard a valid width:

```json
{"width": 20, "height": "invalid"}
```

Only the height receives the corresponding level's default.

Malformed JSON, unreadable files and a non-object root are reported
as configuration errors. They cannot be handled as isolated field
replacements because the document cannot be loaded normally.

### Accepted aliases

The validator accepts these legacy spellings:

| Alias | Canonical key |
| --- | --- |
| `highscor_filename` | `highscore_filename` |
| `points_per_pacgum` | `point_per_pacgum` |
| `points_per_super_pacgum` | `point_per_super_pacgum` |
| `points_per_ghost` | `point_per_ghost` |

Canonical keys take precedence when both forms are present.

### Full-corridor pellet placement

The latest gameplay update constructs `Collectibles` using:

```python
pacgum_count=None
```

This places an ordinary pellet on every reachable floor tile except:

- The player's starting tile.
- The four tiles reserved for power pellets.

In this mode, the `pacgum` configuration key is still recognized,
but it does not limit the number of placed pellets.

This behaviour is intentional and should be considered when changing
maze size or level time.

### Saved user preferences

User preferences are stored separately in:

```text
data/settings.json
```

They include the selected world and display mode.
Older music/SFX keys may remain in saved data even though their
interface switches have been removed.

The configuration file defines game parameters; the settings file
stores user preferences.

## Highscore

### Storage

The leaderboard is stored as JSON at the location configured by
`highscore_filename`.

Example:

```json
[
  {"name": "AHMED", "score": 2500},
  {"name": "SADEEN", "score": 1800}
]
```

### Rules

- Keep the ten highest scores.
- Sort scores in descending order.
- Accept non-negative integer scores.
- Limit names to ten characters.
- Allow alphanumeric characters and spaces.
- Load scores when the game starts.
- Provide name entry after victory or defeat.
- Display saved results through the High Scores screen.

Missing, unreadable or malformed score files must be handled by the
score-loading logic. Save errors are reported through the result
interface rather than being treated as successful writes.

### Why JSON?

JSON is suitable for a small local leaderboard because it:

- Requires no database service.
- Is easy to inspect.
- Supports simple name/score records.
- Is available through Python's standard library.

### Interface

`HighScoresScreen` displays names and scores over the leaderboard
background. The background supplies the table layout, while code
renders current player records.

The leaderboard contains ten result slots below its heading row.
The first-place strip uses the gold asset; subsequent entries use
the secondary strip.

## Maze Generation

### External dependency

The game uses the assigned A-Maze-ing package:

```python
from mazegenerator.mazegenerator import MazeGenerator
```

The external package must remain unchanged. The game's loader and
adapter accommodate its interface.

### Generator parameters

The integration supplies dimensions, a seed and:

```python
perfect=False
```

Imperfect generation permits loops and alternate routes suited to
Pac-Man movement.

The first level uses the configured seed. Later maze generation is
managed by `LevelProgression`.

### Wall-bit representation

| Direction | Bit value |
| --- | --- |
| North | 1 |
| East | 2 |
| South | 4 |
| West | 8 |

A generator cell encodes its walls using these bits.

### Expanded movement grid

The maze layer converts generator cells into floor and wall tiles.

For a W × H generator maze, the expanded model contains:

```text
(2W + 1) × (2H + 1) tiles
```

Therefore, a 20 × 20 generator maze becomes a 41 × 41 tile model.
Only reachable floor tiles are eligible for collectibles.

This explains why 400 pellets do not necessarily fill a 20 × 20
generator maze.

### Failure handling

Generator failures must be handled by the game without modifying
the assigned package. The error path reports a readable message
and prevents normal gameplay from using an invalid maze.

## Implementation

### Application lifecycle

1. Validate command-line usage.
2. Load and normalize the configuration.
3. Initialize Pygame and display management.
4. Initialize assets, themes and screens.
5. Enter the main menu.
6. Process events, update and render the active screen.
7. Release Pygame resources when exiting.

### Movement

Pac-Man receives directional input and moves through open corridors.
Movement follows the maze's floor/wall model.

Ghost movement is autonomous. Ghost state and targeting are separated
from visual rendering.

### Ghost states

| State | Behaviour |
| --- | --- |
| Normal | Uses the configured chasing behaviour |
| Frightened | Becomes edible after a power pellet |
| Eaten | Returns toward its home/revival behaviour |

Ghosts start near the maze corners. Power pellets temporarily change
ghost interactions with the player.

### Collectibles

`Collectibles` discovers floor tiles reachable from the player start.
It reserves four corner positions for power pellets and places ordinary
pellets on the remaining selected positions.

Collection removes each item once and returns it to gameplay for
score and power-effect handling.

### Score and lives

Score increases when collecting pellets or eating edible ghosts.
A harmful ghost collision removes a life.

When lives remain, actors are reset for continued play.
Exhausting all lives ends the game.

### Levels and timing

`LevelProgression` manages the configured level sequence.
Score and remaining lives carry between levels.

The level timer advances during active gameplay. The HUD displays:

- Current score.
- Remaining lives.
- Current level.
- Remaining time.

Pause handling suspends active gameplay progression.

### Results

Victory and defeat lead to the result interface, which displays the
final score and provides player-name entry for the leaderboard.

### Rendering and startup performance

Character assets are prepared for reuse instead of repeatedly loaded
during play.

Maze rendering prepares and caches wall graphics. Small-maze rendering
was adjusted to reduce repeated processing of overlapping wall chunks.

Performance depends on maze dimensions, asset sizes and the target
computer. Development timing output is diagnostic rather than a
guaranteed performance measurement.

## General Software Architecture

### Module responsibilities

| Module or directory | Responsibility |
| --- | --- |
| `pac-man.py` | Application launcher |
| `main.py` | Initialization and main event loop |
| `src/config/` | Configuration parsing and validation |
| `src/entities/` | Player, ghosts and collectible models |
| `src/managers/` | Assets, display, screens and persistence |
| `src/maze/` | Maze adaptation and collision queries |
| `src/systems/` | Gameplay support systems |
| `src/rendering/` | Maze and entity drawing |
| `src/screens/` | Screen-specific events and presentation |
| `src/themes/` | Theme definitions and selection |
| `src/ui/` | Reusable interface elements |

### Main relationships

- `main.py` creates managers and registers screen factories.
- `ScreenManager` selects the active screen and invokes lifecycle hooks.
- Screens implement the `BaseScreen` interface.
- `GameplayScreen` coordinates entities and gameplay systems.
- The maze model supplies movement and collision information.
- Renderers read model state and draw it.
- `AssetManager` loads and caches images.
- `ThemeManager` supplies the active visual theme.
- Persistence managers load and save user data.

### Gameplay systems

| File | Role |
| --- | --- |
| `collectibles.py` | Pellet placement and collection |
| `ghost_ai.py` | Ghost direction and targeting decisions |
| `level_progression.py` | Configured level sequence |
| `cheats.py` | Review assistance |
| `display_layout.py` | Gameplay display planning |

### Screen flow

```text
Main Menu
  → Instructions
  → High Scores
  → Settings
  → Gameplay
      → Pause → Resume / Main Menu
      → Victory or Game Over
          → Name Entry / Score Saving
          → Main Menu
```

### Repository resources

| Location | Contents |
| --- | --- |
| `images/` | UI, maze and character assets |
| `data/` | Saved preferences |
| `plan/` | Planning material |
| `flowcharts/` | Design diagrams |
| `packaging/` | Runtime hook and package instructions |

## Project Management

### Team responsibilities

#### Ahmed Alshoubaki — aalshoub

Ahmed's responsibilities cover game logic and core integration:

- Configuration handling.
- Maze-generator integration.
- Pac-Man movement.
- Ghost behaviour.
- Collision detection.
- Scoring and lives.
- Level progression.
- Integration of gameplay components.

#### Sadeen — sabu-kha

Sadeen's responsibilities cover presentation and screen integration:

- Main menu and navigation.
- Instructions and settings.
- High Scores and result interfaces.
- Pause interface.
- Reusable buttons and interface elements.
- Asset management.
- Maze/entity rendering.
- Ice and Cosmic themes.

Project management documentation is available in [plan/](plan/README.md).

### Planning evidence

Repository planning locations:

- [Planning directory](plan/)
- [Structure plan](plan/struct_file.txt)
- [Flowcharts](flowcharts/)
- [Sadeen's role diagram](flowcharts/sadeens_role.jpeg)

These locations should preserve actual project evidence, including
planning, progress, decisions, problems and acceptance testing.

The currently listed structure plan and role diagram alone do not
establish that all project-management evidence has been documented.

### Documented development issues

Examples addressed during development include:

| Issue | Approach |
| --- | --- |
| Incompatible screen-registration calls | Align screen-manager interfaces |
| Maze-wall orientation and joints | Adjust game-side rendering |
| Slow initial gameplay rendering | Reuse assets and cache prepared walls |
| Highscore text misalignment | Fit text and strips to table positions |
| Settings selecting the wrong theme | Synchronize with the active theme |
| Invalid config fields | Apply independent defaults |
| Sparse random pellet placement | Enable reachable-corridor filling |
| Missing package resources | Include assets and runtime path handling |
| Large generated archive in Git | Exclude build outputs and distribute on Itch.io |

This table describes development work. It is not a substitute for
dated progress records or final acceptance-test results.

## Packaging and Distribution

### Distribution page

https://ahm5edt456.itch.io/pacman

The platform build should be free and unlisted/private with access
available to reviewers.

### Packaging files

| File | Purpose |
| --- | --- |
| `pac-man.spec` | PyInstaller build configuration |
| `build.sh` | Build and archive automation |
| `packaging/runtime_paths.py` | Resolve packaged resource paths |
| `packaging/PLAY_README.txt` | Player instructions included in the archive |

### Build

Activate the project environment:

```bash
source .venv/bin/activate
python -m pip install pyinstaller
bash build.sh
```

Explicitly select its Python interpreter if necessary:

```bash
PYTHON_BIN="$PWD/.venv/bin/python" bash build.sh
```

The script checks required imports, runs PyInstaller, prepares the
launcher and instructions, then creates the distribution archive.

Typical output:

```text
dist/pac-man/
dist/pac-man-linux-x86_64.zip
```

### Test the packaged build

```bash
bash dist/pac-man/play.sh
```

Also download the uploaded archive from Itch.io, extract it into
another directory, and test that copy independently of the repository.

Verify images, navigation, gameplay, preferences and score persistence.

### Review rebuild

The package can be regenerated using:

```bash
bash build.sh
```

Required source, resources and packaging definitions must be present
in the submitted repository.

### Version control

Keep generated output outside Git:

```gitignore
.venv/
__pycache__/
*.pyc
.mypy_cache/
.pytest_cache/
/build/
/dist/
```

Keep the `.spec`, build script and packaging support files tracked.
Distribute the generated ZIP through the game platform.

### Platform considerations

Build separately for each target operating system and architecture.
Linux binaries depend on system libraries, including glibc.

A Fedora build is not guaranteed to run on an older Linux distribution.
Use an appropriate build environment for the systems being supported.

## Validation and Review

The following is an acceptance-test checklist, not a claim that every
check has passed on the final revision.

| Area | Checks |
| --- | --- |
| Launch | Correct argument, missing argument and extra arguments |
| Config loading | Missing file, malformed JSON and hash comments |
| Config validation | Wrong types, missing fields and unknown keys |
| Independent defaults | Invalid field does not reset valid fields |
| Maze integration | Assigned package reinstall and generation failure |
| Movement | Four directions and wall blocking |
| Collectibles | Reachable placement and one-time collection |
| Power pellets | Four positions and frightened effects |
| Ghosts | Movement, harmful contact, edible contact and revival |
| Lives | Decrement, respawn and game over |
| Progression | Level transition, score/lives retention and final victory |
| Timer | Countdown, expiry and pause behaviour |
| Results | Both outcomes, name entry and score saving |
| Leaderboard | Top 10, ordering and malformed-file handling |
| Settings | Theme selection and display changes |
| Packaging | Rebuild, extraction and independent launch |
| Static checks | Flake8 and required mypy flags |

Record actual results and remaining issues in the planning documentation.

The subject's graphical-library restriction requires a separate
review of the functions used. Pygame usage alone does not certify
that every graphical call meets the MLX-equivalence rule.

## Troubleshooting

### No module named pygame

Install requirements using the same interpreter used to launch:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
python pac-man.py config.json
```

### No module named PyInstaller

```bash
python -m pip install pyinstaller
```

Then rerun the build using that interpreter.

### Missing packaging files

Confirm these files exist:

```text
pac-man.spec
packaging/runtime_paths.py
packaging/PLAY_README.txt
```

Copy the complete packaging update, including its directory.

### Assets are missing during source execution

Run from the repository root and verify that the `images/` directory
has been retained with its expected filenames.

### Packaged preferences or scores are not saved

Extract the complete archive into a directory where the current user
has write permission.

### Git rejects the distribution archive

Generated archives belong in `dist/`, which should be ignored by Git.
Upload the game archive to Itch.io and retain the build definitions
in the source repository.

## Architecture and Game Flow Diagrams

The [project diagrams](diagrams/pacman_diagrams.md) explain the software
architecture, screen navigation, configuration loading, maze generation,
gameplay loop, ghost states, data persistence and packaging process.

The diagrams use Mermaid and can be viewed directly on GitHub.

## Resources

- Pac-Man subject, version 1.5, supplied by 42.
- The assigned A-Maze-ing package and its interface.
- [Python documentation](https://docs.python.org/3/)
- [Virtual environments](https://docs.python.org/3/library/venv.html)
- [Python JSON module](https://docs.python.org/3/library/json.html)
- [Pygame Community Edition](https://pyga.me/docs/)
- [Flake8](https://flake8.pycqa.org/en/latest/)
- [mypy](https://mypy.readthedocs.io/en/stable/)
- [PyInstaller](https://pyinstaller.org/en/stable/)
- [Itch.io creator documentation](https://itch.io/docs/creators/)
- [Pac-Man download page](https://ahm5edt456.itch.io/pacman)

### Use of AI

ChatGPT assisted with:

- Explaining Python and project architecture.
- Debugging screen interfaces and integration.
- Configuration validation and error handling.
- Maze adaptation and wall rendering.
- Movement and ghost-related implementation suggestions.
- Collectible placement.
- Interface alignment and visual assets.
- Startup-performance changes.
- Packaging scripts and instructions.
- README drafting.

The contributors remain responsible for understanding retained code,
reviewing generated suggestions, testing the final implementation and
seeking peer review.

No complete lint pass, acceptance-test pass or cross-platform guarantee
is asserted solely by this document.
