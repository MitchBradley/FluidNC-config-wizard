#!/usr/bin/env python3
"""Regenerate boards/index.json, the manifest index.html's dropdown reads.

The wizard is a static site with no server-side directory listing (GitHub
Pages) and no file:// access (browsers block fetch() of local files), so it
can't discover boards/*.board.yaml on its own -- something has to hand it
the list. That's this script's only job: glob boards/*.board.yaml and write
their ids (filename minus ".board.yaml") to boards/index.json as a sorted
JSON array.

Run this after adding, removing, or renaming a board file, then commit the
updated boards/index.json alongside your board.yaml change -- a PR that adds
a board but doesn't update this manifest will build/load fine (index.html
can still load boards/<id>.board.yaml directly, e.g. via the wizard's own
?board=<id> URL param -- see below), it just won't show up in the wizard's
dropdown for anyone else until the manifest catches up.

Usage:
    python3 tools/gen_board_index.py

Testing a new board locally before regenerating this file: you don't need
to run this script first. Serve the repo (python3 -m http.server 8000) and
open index.html?board=<your_new_id> directly -- loadBoard() fetches
boards/<id>.board.yaml straight off disk regardless of what's in
boards/index.json or the dropdown, so you can iterate on a brand-new board
file immediately. Run this script (and commit its output) once, right
before opening your PR, so the board also appears in the dropdown.
"""
import json
import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
BOARDS_DIR = REPO_ROOT / "boards"
OUT_PATH = BOARDS_DIR / "index.json"

SUFFIX = ".board.yaml"


def main():
    ids = sorted(
        p.name[: -len(SUFFIX)]
        for p in BOARDS_DIR.glob(f"*{SUFFIX}")
    )
    OUT_PATH.write_text(json.dumps(ids, indent=2) + "\n")
    print(f"Wrote {OUT_PATH.relative_to(REPO_ROOT)} with {len(ids)} board id(s):")
    for i in ids:
        print(f"  {i}")


if __name__ == "__main__":
    main()
