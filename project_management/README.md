# Project Management — Pac-Man

This directory records team responsibilities, development progress, technical
choices, risks and acceptance testing for the Pac-Man project.

These records were consolidated retrospectively from the team's development
work. They are not an original dated schedule or a record of daily meetings.
No planned dates, meeting minutes or successful tests have been invented.

## Documents

| Document | Purpose |
| --- | --- |
| [Team organization](team_organization.md) | Ownership, integration and decision responsibilities |
| [Timeline and progress](timeline_and_progress.md) | Development stages and evidenced progress |
| [Technical decisions](technical_decisions.md) | Choices, reasons and consequences |
| [Risks](risk_register.md) | Risks, mitigations and unresolved checks |
| [Acceptance testing](acceptance_test_plan.md) | Repeatable manual and static checks |
| [Issues and blockers](issues_and_blockers.md) | Problems encountered and resolution evidence |

Existing design references: [structure plan](struct_file.txt) and
[Sadeen's role diagram](../flowcharts/sadeens_role.jpeg).
These files are referenced from the supplied repository structure; they are not
included or replaced by this documentation package.

## Project information

- Contributors: Ahmed Alshoubaki (`aalshoub`) and Sadeen (`sabu-kha`).
- Language and rendering: Python and Pygame Community Edition.
- Visual themes: Ice and Cosmic.
- Maze generation: assigned external A-Maze-ing package, used unchanged.
- Distribution: [Itch.io](https://ahm5edt456.itch.io/pacman).
- Submission target: Pac-Man subject version 1.5.

## Evidence conventions

- **Reported successful:** a contributor explicitly reported success.
- **Implementation updated:** code or configuration was changed; this does not
  establish a complete acceptance-test pass.
- **Pending verification:** repeat the check on the final submission revision.

Record final test evidence against a Git commit. Neither these documents nor
the presence of a feature in source proves that the final build passes review.

## README integration

Link this directory from the root README's Project Management section:

```markdown
Project planning, team organization, decisions, risks and acceptance testing
are documented in [plan/](plan/README.md).
```
