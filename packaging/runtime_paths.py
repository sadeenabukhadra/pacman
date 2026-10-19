"""Keep embedded assets temporary and player data persistent in frozen builds."""

import os
from pathlib import Path
import sys


def configure_frozen_paths() -> None:
    """Prepare bundled defaults and redirect relative persistence paths."""
    if not getattr(sys, "frozen", False):
        return
    bundle = Path(getattr(sys, "_MEIPASS"))
    caller = Path.cwd()
    data_base = Path(os.environ.get("XDG_DATA_HOME", ""))
    if not data_base.is_absolute():
        data_base = Path.home() / ".local" / "share"
    saves = data_base / "pacman-42"
    try:
        saves.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        print(f"ERROR: Cannot create game save directory: {error}",
              file=sys.stderr)
        raise SystemExit(1) from error

    if len(sys.argv) == 1:
        sys.argv.append(str(bundle / "config.json"))
    elif len(sys.argv) == 2:
        config = Path(sys.argv[1]).expanduser()
        sys.argv[1] = str(config if config.is_absolute() else caller / config)

    # Relative image/font paths and module-relative paths now share the bundle.
    os.chdir(bundle)
    from src.managers import score_manager, settings_manager

    settings_manager.SETTINGS_FILE = saves / "settings.json"
    score_manager.SCORE_FILE = saves / "high_scor.json"
    original = getattr(score_manager, "configure_scores", None)
    if original is not None:
        def configure_scores(filename: str) -> None:
            """Resolve configured relative score paths under persistent data."""
            path = Path(filename).expanduser()
            if not path.is_absolute():
                path = saves / path
            original(str(path))

        score_manager.configure_scores = configure_scores


configure_frozen_paths()
