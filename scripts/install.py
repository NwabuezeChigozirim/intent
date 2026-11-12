#!/usr/bin/env python3
"""Install this plugin for Cursor as a local plugin.

Copies the plugin into ~/.cursor/plugins/local/planning. Run it again after pulling
changes. Standard library only; Linux, macOS and Windows.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil

SOURCE = Path(__file__).resolve().parents[1]
NAME = "planning"
PARTS = (".cursor-plugin", "skills", "README.md", "LICENSE", "THIRD_PARTY_LICENSE-mattpocock-skills")
SKIP = shutil.ignore_patterns("__pycache__", "*.pyc", "node_modules")


def install(target: Path) -> Path:
    if target.is_symlink() or target.is_file():
        target.unlink()
    elif target.exists():
        marker = target / ".cursor-plugin" / "plugin.json"
        if not marker.is_file() or json.loads(marker.read_text(encoding="utf-8")).get("name") != NAME:
            raise SystemExit(f"refusing to replace {target}: it is not a previous install of this plugin")
        shutil.rmtree(target)
    target.mkdir(parents=True)
    for name in PARTS:
        source = SOURCE / name
        if source.is_dir():
            shutil.copytree(source, target / name, ignore=SKIP)
        else:
            shutil.copy2(source, target / name)
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--target", default=str(Path.home() / ".cursor" / "plugins" / "local" / NAME),
                        help="where to install (default: Cursor's local plugin directory)")
    args = parser.parse_args()
    target = install(Path(args.target).expanduser())
    print(f"installed: {target}")
    if not (target.parent / "governance").exists():
        print("note: the governance plugin is not installed beside it; /implement needs it.")
    print("Restart Cursor, run /setup-planning once in each project, then start with /grill-with-docs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
