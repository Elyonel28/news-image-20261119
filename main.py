#!/usr/bin/env python3
"""news-image-20261119 entrypoint (Python 3.13, standard library only).

The entry is a single image, entry.png, drawn in this repository
(see README.md for how it was made). This program copies it to the
grader's output directory as entry.png. It uses no network and is
deterministic: every run writes the same bytes.

Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))

OUT.mkdir(parents=True, exist_ok=True)
shutil.copyfile(HERE / "entry.png", OUT / "entry.png")
