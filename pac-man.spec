# -*- mode: python ; coding: utf-8 -*-
"""Build a single executable with embedded resources."""

from pathlib import Path

root = Path(SPECPATH)

datas = [
    (str(root / "images"), "images"),
    (str(root / "config.json"), "."),
]

datas.append((str(root / "packaging" / "PLAY_README.txt"), "."))

for folder in ("fonts", "sounds"):
    if (root / folder).is_dir():
        datas.append((str(root / folder), folder))

a = Analysis(
    [str(root / "pac-man.py")],
    pathex=[str(root)],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[
        str(root / "packaging" / "runtime_paths.py"),
    ],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="pac-man",
    debug=False,
    strip=False,
    upx=False,
    console=True,
)
