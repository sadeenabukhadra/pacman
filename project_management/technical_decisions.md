# Technical Decisions

## D01 — Separate gameplay, screens and rendering

Use dedicated modules for entities, systems, screens, managers and renderers.
This keeps game rules separate from visual presentation and lets Ice/Cosmic
assets share the same gameplay model. The cost is keeping interfaces and
coordinate conventions consistent across modules.

## D02 — Use the assigned generator unchanged

Adapt game-side code to `MazeGenerator` instead of changing the external package.
Generate with `perfect=False`. This respects the subject and allows reviewers
to reinstall the assigned package. Integration must still be checked after
reinstallation; a bundled source directory alone is insufficient evidence.

## D03 — Expand generator cells into movement tiles

Convert wall-bit cells to a wall/floor model with dimensions
`(2W + 1) × (2H + 1)`. Movement, reachability and collectibles operate on this
expanded model. Generator cell count therefore differs from available floor
positions; pellet count cannot be calculated as W multiplied by H.

## D04 — Validate configuration fields independently

Use each field's own default when it is missing, has the wrong type or is outside
its supported range. Preserve other valid fields, including valid dimensions
in the same level. Ignore unknown keys and accept documented legacy aliases.
Malformed JSON is a document-level error rather than an individual-field error.

## D05 — Fill reachable corridors with pellets

The latest gameplay change passes `pacgum_count=None`. The collectibles system
fills reachable floor tiles except the player start and four power-pellet tiles.
This removes sparse random placement. Consequence: the recognized `pacgum`
config field no longer limits placement in this mode. Document this explicitly
and reassess level-time balance; do not present that field as an active limit.

## D06 — Store local highscores in JSON

A small Top 10 leaderboard needs no database service. JSON is readable and
available in the standard library. Validate names/scores and report read/write
failures. Persistence depends on a writable save location.

## D07 — Reuse prepared graphics

Prepare character sprites for reuse and cache maze-wall graphics to reduce
startup work and repeated drawing preparation. Timing identified wall preparation
as a significant contributor. Measurements from different machines and test
mazes are not interchangeable performance guarantees.

## D08 — Simplify Settings

Keep Ice/Cosmic selection and display mode, removing Music/Sound Effects switches.
Select the active theme when entering the screen. Old audio preference keys may
remain in saved settings for compatibility; their presence does not mean audio
controls or playback are implemented.

## D09 — Package as a portable Linux directory

Use PyInstaller via a root `.spec` and `build.sh`. Include assets, configuration,
launcher and instructions. A runtime hook handles packaged resource paths.
Tradeoffs include larger archives, write-permission requirements and Linux
system-library compatibility. Build separately for other operating systems.

## D10 — Separate distribution artifacts from Git source

Keep source, assets and build definitions in Git. Exclude generated `build/`
and `dist/`. Distribute the complete archive through Itch.io. This also avoids
the large-file rejection encountered when pushing the generated ZIP.
