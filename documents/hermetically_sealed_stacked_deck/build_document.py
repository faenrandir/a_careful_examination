#!/usr/bin/env python

import subprocess
from pathlib import Path

svgz_paths = list(Path.cwd().glob("*.svgz"))

to_convert_to_png = [path for path in svgz_paths if "standalone" not in path.name]

MEDIA_DIR = Path.cwd() / "../../media"

base_cmd = ["svg-to-png", "--export-dpi", "200", "--bkg", "white"]

png_paths = []
for path in to_convert_to_png:
    cmd = base_cmd + [str(path)]
    subprocess.run(cmd)
    png_paths.append(path.with_suffix(".png"))

for path in png_paths:
    new_path = MEDIA_DIR / path.name
    path.rename(new_path)
