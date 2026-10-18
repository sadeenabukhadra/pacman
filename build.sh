#!/usr/bin/env bash
# Build from the project's active Python environment.
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
PYTHON_BIN="${PYTHON_BIN:-python}"
"$PYTHON_BIN" -c 'import PyInstaller, pygame, mazegenerator.mazegenerator' || {
    echo 'Missing build dependencies. Activate your venv, then install pygame-ce, pyinstaller and the assigned maze package.' >&2
    exit 1
}
"$PYTHON_BIN" -m PyInstaller --clean --noconfirm pac-man.spec
"$PYTHON_BIN" - <<'PY'
from pathlib import Path
import platform
import shutil
import stat

folder = Path('dist/pac-man')
(folder / 'data').mkdir(exist_ok=True)
launcher = folder / 'play.sh'
launcher.write_text('''#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
if [ "$#" -eq 0 ]; then
    set -- config.json
fi
exec ./pac-man "$@"
''')
launcher.chmod(launcher.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
shutil.copyfile('packaging/PLAY_README.txt', folder / 'PLAY_README.txt')
archive = shutil.make_archive(
    f'dist/pac-man-{platform.system().lower()}-{platform.machine()}',
    'zip', root_dir='dist', base_dir='pac-man',
)
print(f'Package ready: {archive}')
PY
