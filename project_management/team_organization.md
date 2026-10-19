# Team Organization

## Responsibility split

| Contributor | Primary scope | Relevant components |
| --- | --- | --- |
| Ahmed Alshoubaki — aalshoub | Core gameplay and integration | Configuration, maze adaptation, movement, ghost behaviour, collisions, scoring, lives, progression |
| Sadeen — sabu-kha | UI, graphics and screen management | Screens, buttons, assets, renderers, Ice/Cosmic themes, menu navigation |

The split describes primary responsibility, not exclusive authorship of every
line. Integration crosses both areas.

## Ahmed's responsibilities

- Integrate the assigned generator without modifying its implementation.
- Keep movement and collisions consistent with the adapted maze model.
- Coordinate ghost states, collectibles, scoring and life loss.
- Connect level progression and configuration to active gameplay.
- Handle failures in configuration and generation cleanly.

## Sadeen's responsibilities

- Implement screen layouts and navigation.
- Prepare consistent Ice and Cosmic assets.
- Align buttons, tables, text and selection indicators.
- Render maze walls, actors and collectibles consistently.
- Connect interface actions to the shared screen and display managers.

## Integration boundaries

| Boundary | Agreement required |
| --- | --- |
| Screen factories | Constructor arguments and transition callbacks |
| Maze model | Coordinate system and wall/floor queries |
| Rendering | Tile origin, tile dimensions and actor coordinates |
| Results | Final score, win/loss state and score-saving flow |
| Settings | Active theme and display-mode application |
| Packaging | Resource locations and writable persistence paths |

## Decision evidence

The issue log and decision log describe changes visible during development.
The available record does not establish a formal meeting cadence, voting
process or issue-assignment tool, so none is claimed here.

## Recommended final handoff

Before submission, both contributors should demonstrate their own components
and explain the interfaces between gameplay and presentation. Agree on one
submission commit and test the package built from that commit.
This is a handoff checklist, not a claim that the handoff has occurred.
