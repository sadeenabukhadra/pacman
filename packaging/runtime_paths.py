"""Resolve game paths before importing the packaged application."""

import os
from pathlib import Path
import sys

if getattr(sys, "frozen", False):
    if len(sys.argv) == 2:
        sys.argv[1] = str(Path(sys.argv[1]).resolve())
    os.chdir(Path(sys.executable).resolve().parent)
