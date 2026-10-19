# Risk Register

Likelihood and impact below are qualitative planning assessments, not measured
probabilities. No risk is considered closed solely because code was changed.

| ID | Risk | Likelihood / impact | Mitigation | Verification owner / state |
| --- | --- | --- | --- | --- |
| R01 | Generator reinstall exposes an interface mismatch | Medium / High | Keep assigned package unchanged; test game-side adapter after reinstall | Ahmed; pending final check |
| R02 | Invalid config resets valid settings or crashes launch | Medium / High | Independent defaults; malformed-file messages; targeted tests | Ahmed; update prepared, final check pending |
| R03 | Movement and rendered walls disagree | Medium / High | Shared tile geometry; test corners and narrow passages | Both; final gameplay check pending |
| R04 | Highscore save failure traps the player | Medium / High | Test unwritable path and navigation after failure | Both; pending verification |
| R05 | Package misses assets or uses wrong paths | Medium / High | Include resources and runtime hook; test extracted copy | Sadeen with Ahmed; build reported successful |
| R06 | Linux build fails on older distributions | Medium / High | Build on oldest supported target and test there | Both; compatibility scope unverified |
| R07 | Full-corridor pellets exceed practical timer balance | High / Medium | Play representative sizes; adjust config based on observed completion time | Ahmed; pending play test |
| R08 | Static-check failures remain in final code | Medium / High | Run required lint flags on submission commit | Both; final pass unrecorded |
| R09 | Theme or fullscreen selection differs from actual state | Medium / Medium | Test entry, save, reopen and restart | Sadeen; fixes prepared, final check pending |
| R10 | Generated ZIP is committed to source repository | Previously encountered / Medium | Ignore build output; inspect tracked paths before push | Both; final Git check pending |
| R11 | Download page is inaccessible to reviewers | Medium / High | Free unlisted/private setup; test supplied link anonymously | Both; link supplied, download check pending |
| R12 | Management evidence overstates completed work | Medium / Medium | Separate retrospective records, proposed checks and verified outcomes | Both; review these records before submission |
| R13 | Used graphical APIs fail MLX-equivalence requirement | Unassessed / High | Review actual used functions against subject restriction | Both; separate API review pending |

## Priority before review

Resolve high-impact functional checks first: launch/config, generator integration,
movement, results/persistence, required static checks and independent package
launch. Record any remaining limitations rather than marking them passed.
