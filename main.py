#!/usr/bin/env python3
"""Copy the entry image to the output directory.

entry.png is the world-news infographic for 19 November 2026. The program
runs with no network. It copies the repository's entry.png to
/output/entry.png, creating /output when needed.
"""

import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
DST = "/output/entry.png"


def main():
    os.makedirs(os.path.dirname(DST), exist_ok=True)
    # The output must be byte-identical to entry.png.
    shutil.copyfile(SRC, DST)
    print(f"wrote {DST}")


if __name__ == "__main__":
    main()
