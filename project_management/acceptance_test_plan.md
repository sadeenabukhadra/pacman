# Acceptance Test Plan

## Purpose and execution record

Verify the final Pac-Man submission against the subject and current behaviour.
This is a test plan; the cases below are **not executed here**.

Before execution, record:

- Submission Git commit: not recorded.
- Tester and date: not recorded.
- Operating system / Python / pygame-ce: not recorded for final run.
- Source or downloaded package: not recorded.
- Actual result, evidence and issue reference for each case.

Use a temporary config and score location for failure cases. Preserve real
player data. Re-run failed cases after fixes and retain the previous result.

## Acceptance cases

| ID | Procedure | Expected result | Status |
| --- | --- | --- | --- |
| A01 | Run `python3 pac-man.py config.json` | Opens main menu with supplied valid config | Not executed |
| A02 | Launch with no argument and with two arguments | Clear usage error; no traceback | Not executed |
| A03 | Supply a missing config or malformed JSON | Clear error; no unhandled exception | Not executed |
| A04 | Add full-line hash comments | Loads config successfully | Not executed |
| A05 | Make lives invalid while keeping theme/score/time valid | Only lives uses its default; other values remain | Not executed |
| A06 | Make one level height invalid, keep width valid | Only invalid dimension is replaced | Not executed |
| A07 | Supply booleans, strings and negatives for integer fields | Applies documented field defaults; no crash | Not executed |
| A08 | Add unknown keys and legacy aliases | Unknown keys ignored; documented aliases work | Not executed |
| A09 | Reinstall assigned generator unchanged and launch | Integration works with assigned API | Not executed |
| A10 | Trigger a controlled generator failure in a test environment | Reports failure cleanly | Not executed |
| A11 | Repeat first level with same seed and dimensions | Initial maze is reproducible | Not executed |
| A12 | Complete levels using review tools | Later levels progress; score/lives retained; final victory shown | Not executed |
| A13 | Move with arrows and WASD; push toward walls | Four directions work; no wall traversal | Not executed |
| A14 | Inspect full-corridor pellet placement | Reachable floor covered except start and four power positions | Not executed |
| A15 | Collect ordinary pellet twice at same position | Score increases once; pellet disappears | Not executed |
| A16 | Collect each power pellet | Score increases; ghosts become temporarily edible | Not executed |
| A17 | Observe ghosts in normal and frightened states | Autonomous corridor movement; chase/run-away behaviour | Not executed |
| A18 | Eat a frightened ghost and wait for revival | Points awarded; ghost returns/revives appropriately | Not executed |
| A19 | Touch harmful ghost, then exhaust lives | One life lost per handled collision; respawn; eventual game over | Not executed |
| A20 | Pause, wait and resume | Active game state/timer do not advance while paused | Not executed |
| A21 | Let timer expire | Defined time-expiry outcome occurs cleanly | Not executed |
| A22 | Inspect HUD during representative levels | Score, lives, level and remaining time visible | Not executed |
| A23 | Finish both win and loss flows | Final score and name entry available; return to menu works | Not executed |
| A24 | Enter empty, overlong or disallowed names; invalid scores in tests | Validation enforces documented limits | Not executed |
| A25 | Save more than ten results, restart and open leaderboard | Top ten sorted descending and persisted | Not executed |
| A26 | Use missing/malformed score file and unwritable score path | Loading recovers; save failure reported without trapping navigation | Not executed |
| A27 | Change theme/display; save, reopen and restart | Actual display and selection match saved/active state | Not executed |
| A28 | Exercise review cheat controls | Facilitate review without corrupting screen transitions | Not executed |
| A29 | Run required `make lint` | Flake8 and required mypy checks succeed | Not executed |
| A30 | Rebuild using `bash build.sh` | Complete executable directory and ZIP generated | Not executed |
| A31 | Download from Itch.io anonymously and extract elsewhere | Page/download accessible; package launches independently | Not executed |
| A32 | Save scores/settings from extracted package and relaunch | Data persists in a writable location | Not executed |
| A33 | Audit used graphics functions against MLX equivalents | Used calls comply with the subject restriction | Not executed |

## Evidence already available

- The contributor reported successful package creation on October 18, 2026.
- Focused development checks were reported for independent config defaults and
  source syntax. These do not establish a final full-project test pass.
- No complete final lint result or independent downloaded-build play test is
  retained in this documentation.

## Completion criteria

Mark each executed case with its actual outcome. Record failures in the issue
log, including reproduction steps and retest evidence. Do not convert a planned
case into a pass merely because its feature exists in code.
