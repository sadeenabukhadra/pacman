# Pac-Man — Architecture and Game Flow

This document explains the project using Mermaid diagrams. Open it on GitHub
or in a Markdown viewer with Mermaid support to see the rendered diagrams.

The diagrams describe the latest supplied project structure and discussed
updates. They are architectural documentation, not proof of a complete runtime
test or a fresh audit of every source file.

## 1. Application Architecture

```mermaid
flowchart TD
    Entry["pac-man.py"] --> Main["main.py"]
    Main --> Config["Configuration loader and validator"]
    Main --> Managers["Screen, display, theme and asset managers"]
    Managers --> Screens["Menus and screens"]
    Screens --> Gameplay["GameplayScreen"]
    Gameplay --> Models["Maze, Pacman and Ghost entities"]
    Gameplay --> Systems["Collectibles, AI, levels and cheats"]
    Gameplay --> Rendering["MazeRenderer and EntityRenderer"]
    Rendering --> Assets["Images and theme definitions"]
    Screens --> Persistence["Score and settings managers"]
    Persistence --> Files["JSON files"]
```

`main.py` assembles components and runs the application loop. Screens handle
screen-specific input and presentation. Gameplay coordinates state and systems;
renderers display that state. Persistence is delegated to managers.

## 2. Screen Navigation

```mermaid
flowchart TD
    Menu["Main Menu"] --> Start["Start Game"]
    Menu --> Instructions["Instructions"]
    Menu --> Scores["High Scores"]
    Menu --> Settings["Settings"]
    Menu --> Quit["Exit application"]
    Instructions --> Menu
    Scores --> Menu
    Settings --> Menu
    Start --> Game["Gameplay"]
    Game --> Pause["Pause Menu"]
    Pause -->|Resume| Game
    Pause -->|Return| Menu
    Game --> Result["Victory or Game Over"]
    Result --> Name["Enter player name"]
    Name --> Save["Validate and save score"]
    Save --> Menu
```

The result path represents the intended successful save flow. Save-error
recovery and additional navigation depend on the result-screen implementation.

## 3. Configuration and Startup

```mermaid
flowchart TD
    Launch["Launch with one JSON argument"] --> Args{"Argument valid?"}
    Args -->|No| Error["Show clear error and exit"]
    Args -->|Yes| Read["Read config and remove hash-comment lines"]
    Read --> Parsed{"Readable JSON object?"}
    Parsed -->|No| Error
    Parsed -->|Yes| Fields["Validate fields independently"]
    Fields --> Valid{"Field valid?"}
    Valid -->|Yes| Keep["Keep supplied value"]
    Valid -->|No| Default["Use that field's default"]
    Keep --> Merge["Assemble GameConfig"]
    Default --> Merge
    Merge --> Init["Initialize display, managers and sprites"]
    Init --> Register["Register screen factories"]
    Register --> Menu["Show Main Menu"]
```

Unknown keys are ignored. Invalid dimensions are handled independently within
each level. Broken JSON syntax is a document-level error, not a field default.

## 4. Maze and Level Preparation

```mermaid
flowchart TD
    Request["Prepare configured level"] --> Parameters["Dimensions and seed"]
    Parameters --> Generator["Assigned MazeGenerator: perfect=False"]
    Generator --> Success{"Generation succeeds?"}
    Success -->|No| Error["Report generation failure"]
    Success -->|Yes| Bits["Wall-bit cell grid"]
    Bits --> Adapt["Adapt into Maze wall/floor tiles"]
    Adapt --> Spawn["Choose player and ghost positions"]
    Spawn --> Reachable["Find floor reachable from player"]
    Reachable --> Power["Reserve four corner power-pellet positions"]
    Power --> Pellets["Fill remaining floor with ordinary pellets"]
    Pellets --> Ready["Prepare timer, HUD and renderers"]
    Ready --> Game["Begin gameplay"]
```

A generator maze of W × H cells expands into `(2W + 1) × (2H + 1)` movement
tiles. The external generator remains unchanged. The first maze uses the
configured seed; later-level preparation is coordinated by `LevelProgression`.

The latest pellet update uses `pacgum_count=None`, so every reachable floor tile
receives a pellet except the player start and four power-pellet positions. The
numeric `pacgum` config field does not limit placement in that mode.

## 5. Main Loop

```mermaid
flowchart TD
    Frame["Next frame"] --> Events["Read events"]
    Events --> Dispatch["Active screen handles input"]
    Dispatch --> Exit{"Exit requested?"}
    Exit -->|Yes| Cleanup["Quit Pygame and exit"]
    Exit -->|No| Update["Update active screen using dt"]
    Update --> Render["Render active screen"]
    Render --> Present["Update display and limit frame rate"]
    Present --> Frame
```

Each screen follows the common event/update/render interface. Pausing preserves
the active run and suspends gameplay progression while pause input is handled.

## 6. Gameplay Decisions

```mermaid
flowchart TD
    Update["Gameplay update"] --> Paused{"Paused?"}
    Paused -->|Yes| Wait["Wait for resume or menu action"]
    Paused -->|No| Move["Advance actors and gameplay systems"]
    Move --> Pickup["Collect pellets and apply points/effects"]
    Pickup --> Contact{"Ghost contact?"}
    Contact -->|No| Goals["Check timer and remaining pellets"]
    Contact -->|Edible ghost| Eat["Award ghost points; enter eaten state"]
    Contact -->|Harmful ghost| Life["Remove life unless protected"]
    Eat --> Goals
    Life --> Lives{"Lives remain?"}
    Lives -->|No| Lose["Game Over"]
    Lives -->|Yes| Reset["Reset actors and apply respawn protection"]
    Reset --> Goals
    Goals --> Outcome{"Level outcome?"}
    Outcome -->|Time expired| Lose
    Outcome -->|Still active| Continue["Continue gameplay"]
    Outcome -->|All pellets collected| More{"More levels?"}
    More -->|Yes| Next["Prepare next level; retain score and lives"]
    More -->|No| Win["Victory"]
```

This diagram summarizes decisions rather than the exact order of every
collision substep. The implementation collects and checks contacts in small
movement steps to reduce missed interactions. Cheat states may override normal
life-loss, speed, timing or progression behaviour.

## 7. Ghost Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Normal
    Normal --> Frightened: Power pellet
    Frightened --> Normal: Fright duration expires
    Frightened --> Eaten: Player eats ghost
    Eaten --> Normal: Return and revival complete
    Normal --> [*]: Run ends
    Frightened --> [*]: Run ends
    Eaten --> [*]: Run ends
```

Normal ghosts pursue the player using their AI rules. Frightened ghosts are
edible and should flee. Eaten ghosts return toward home before revival.

## 8. Scores and Preferences

```mermaid
flowchart TD
    Result["Game ends with final score"] --> Entry["Player enters name"]
    Entry --> Validate{"Valid name and score?"}
    Validate -->|No| Feedback["Show validation feedback"]
    Feedback --> Entry
    Validate -->|Yes| Load["Load existing scores safely"]
    Load --> Top["Add result, sort and retain Top 10"]
    Top --> Write{"Write succeeds?"}
    Write -->|No| Failure["Report save failure"]
    Write -->|Yes| Saved["Saved leaderboard"]
    Saved --> View["High Scores screen"]
    Settings["Settings screen"] --> Preferences["Save theme and display preferences"]
    Preferences --> SettingsFile["data/settings.json"]
```

Score location comes from `highscore_filename`. Names have a ten-character
limit and allow alphanumeric characters and spaces; scores are non-negative
integers. The failure node does not assert a particular retry/navigation policy.

## 9. Packaging and Distribution

```mermaid
flowchart TD
    Source["Source, assets and assigned dependency"] --> Build["build.sh"]
    Spec["pac-man.spec"] --> Build
    Hook["packaging/runtime_paths.py"] --> Build
    Build --> Bundle["PyInstaller executable directory"]
    Instructions["packaging/PLAY_README.txt"] --> Archive["Launcher, instructions and ZIP"]
    Bundle --> Archive
    Archive --> Test["Extract and test independently"]
    Test --> Upload["Upload Linux ZIP to Itch.io"]
    Upload --> Download["Player downloads complete archive"]
    Download --> Run["Extract and run play.sh"]
```

Build definitions stay in Git. Generated `build/` and `dist/` output should be
ignored. The build targets the operating system/architecture used to produce
it; Linux system-library compatibility still needs testing.

Game page: https://ahm5edt456.itch.io/pacman

## 10. Responsibility Map

| Contributor | Main responsibilities | Integration points |
| --- | --- | --- |
| Ahmed Alshoubaki — aalshoub | Configuration, generator integration, movement, AI, collisions, scoring, lives and levels | Maze coordinates, gameplay state and screen callbacks |
| Sadeen — sabu-kha | Screens, navigation, assets, rendering and Ice/Cosmic presentation | Screen interfaces, display geometry, themes and persistence UI |

The map describes primary responsibilities, not exclusive ownership of all code.
Both contributors need to understand how their components connect.

## Add to the Root README

```markdown
Architecture, screen transitions, gameplay and packaging diagrams are available
in [diagrams/pacman_diagrams.md](diagrams/pacman_diagrams.md).
```
