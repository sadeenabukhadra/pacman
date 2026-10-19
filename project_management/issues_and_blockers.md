# Issues and Blockers

This retrospective log consolidates problems evidenced during development.
"Updated" means a change was prepared, not that every final scenario passed.

| ID | Problem | Action / outcome | Remaining evidence |
| --- | --- | --- | --- |
| I01 | ScreenManager lacked registration method expected by main | Added/aligned registration interface | Test complete screen navigation on final revision |
| I02 | MenuScreen constructor missed transition callback | Aligned construction with callback argument | Regression navigation test |
| I03 | Maze wall pieces had orientation, scale and joint problems | Iterated renderer rotations and placement | Final Ice/Cosmic visual inspection |
| I04 | Start Game had noticeable delay | Measured startup; reused sprite preparation and reduced overlapping small-maze work | Final target-machine timing |
| I05 | Leaderboard text/strips did not align with new background | Fitted result rows and centered score column | Inspect ten entries at actual window size |
| I06 | Settings highlighted saved Ice despite active theme | Synchronize on construction and entry | Test reopen and restart |
| I07 | Audio controls no longer desired | Removed Music/Sound Effects controls; centered display-mode bar | Final input/layout check |
| I08 | Invalid numeric config fields needed independent defaults | Updated validator to use each invalid field's default | End-to-end config launch cases |
| I09 | Requested pellet count produced sparse random positions | Enabled existing full-corridor mode with `pacgum_count=None` | Verify coverage and timer balance; document inactive count limit |
| I10 | PyInstaller missing from active interpreter | Installed build tool and selected venv Python explicitly | Repeat from documented clean environment |
| I11 | Build missing runtime hook and package instructions | Added `runtime_paths.py` and `PLAY_README.txt` | Contributor subsequently reported build success |
| I12 | Git push rejected oversized distribution ZIP | Recommended ignoring/removing generated output from tracking | Successful final push not recorded |
| I13 | Itch.io upload blocked by unverified email | Identified account verification requirement | Game page later supplied; downloaded build test pending |
| I14 | Required mypy check reported project and external-package errors | Type fixes and external-package exclusion were discussed | Final complete lint output not retained |
| I15 | Missing pygame caused import traceback | Provided launcher-level missing-module handling | Test using interpreter without pygame |

## Performance measurement evidence

One contributor startup run reported:

| Phase | Reported duration |
| --- | --- |
| Maze generation | 46.1 ms |
| Gameplay setup | 5.0 ms |
| Background/theme preparation | 32.5 ms |
| Wall chunks | 416.3 ms |
| First gameplay render | 510.0 ms |
| Total until first frame | 563.5 ms |

Some phases are nested, so these rows must not be summed. Wall preparation
was identified as the main measured contributor. A later optimization was
prepared; no final target-machine timing is asserted here.

## Remaining blockers and checks

- Final full-project lint result is not recorded here.
- Final gameplay acceptance results are not recorded here.
- Anonymous download and play verification is not recorded here.
- The graphical-function equivalence audit remains a separate requirement.
- Original scheduling records were not retained in the provided evidence.

## Team conflicts

No interpersonal conflict or formal conflict-resolution event is documented in
the available development record. Do not invent one to populate this section.
Technical integration problems are recorded above.

## Add future issues

For each new issue record: observed behaviour, reproduction steps, expected
behaviour, owner, fix commit, actual retest result and supporting evidence.
