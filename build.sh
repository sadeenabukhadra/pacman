#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
PYTHON_BIN="${PYTHON_BIN:-$PWD/.venv/bin/python}"
if [ ! -x "$PYTHON_BIN" ]; then
  echo "ERROR: Activate/install .venv or set PYTHON_BIN." >&2
  exit 1
fi
"$PYTHON_BIN" -c 'import PyInstaller, pygame, mazegenerator.mazegenerator'
# A separate output avoids collisions with previous dist/pac-man directories.
"$PYTHON_BIN" -m PyInstaller --clean --noconfirm \
  --distpath dist --workpath build pac-man.spec
"$PYTHON_BIN" - <<'PY'
from pathlib import Path
import platform
import zipfile

folder = Path('dist')
launcher = folder / 'play.sh'
launcher.write_text('''#!/usr/bin/env bash
set -euo pipefail
GAME_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
if [ "${1:-}" = "--help" ]; then
    cat <<'HELP'
PAC-MAN — Linux
Run: bash play.sh
Custom config: bash play.sh /path/to/config.json
Move: arrow keys or WASD. See Instructions for game rules.
Settings: Ice/Cosmic and fullscreen/windowed mode.
Saves: ${XDG_DATA_HOME:-~/.local/share}/pacman-42/
Default config and assets are embedded. No Python installation required.
Keep both files together. Linux compatibility depends on system libraries.
HELP
    exit 0
fi
exec "$GAME_DIR/pac-man" "$@"
''', encoding='utf-8')
launcher.chmod(0o755)
archive = folder / f'pac-man-{platform.system().lower()}-{platform.machine()}.zip'
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as output:
    output.write(folder / 'pac-man', 'pac-man')
    output.write(launcher, 'play.sh')
print(f'Package ready: {archive}')
print('ZIP contains exactly pac-man and play.sh.')
PY
