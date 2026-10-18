# -*- mode: python ; coding: utf-8 -*-
"""Build a portable directory with assets beside the executable."""
from pathlib import Path

root = Path(SPECPATH)
datas = [(str(root / "images"), "images"),
         (str(root / "config.json"), ".")]
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
    runtime_hooks=[str(root / "packaging" / "runtime_paths.py")],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, [],
    exclude_binaries=True,
    name="pac-man",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    contents_directory=".",
)
coll = COLLECT(
    exe, a.binaries, a.datas,
    strip=False, upx=False, name="pac-man",
)
