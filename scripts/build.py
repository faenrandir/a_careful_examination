#!/usr/bin/env python3
"""Build the site into docs/ (§I.1).

This is the one build pipeline. scripts/serve.py and scripts/release.py both
call build() (§V.2), so the preview and the published site are built the same
way. It does not run update_dates.py: a preview must not edit content, so
release.py runs that step itself before building.

Usage: python3 scripts/build.py
"""

import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS = REPO_ROOT / "docs"

# Post-processing scripts, run in this order after `zola build`.
POST_BUILD_SCRIPTS = (
    "scripts/fix_links.py",
    "scripts/generate_search_index.py",
    "scripts/generate_taxonomy_index.py",
)


def run(cmd: list[str]) -> None:
    """Run a command from the repository root, printing it first; raise on failure."""
    print(f"  $ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    if result.returncode != 0:
        if result.stdout:
            print(result.stdout.strip())
        if result.stderr:
            print(result.stderr.strip(), file=sys.stderr)
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")


def build() -> None:
    """Clean-build the site into docs/ and run the post-build steps (§V.1)."""
    print("=== Building site ===")
    shutil.rmtree(DOCS, ignore_errors=True)
    run(["zola", "build"])

    # Zola already copies static/ into docs/. The earlier pipeline also copied
    # these two folders explicitly, and this keeps that step unchanged.
    for name in ("documents", "images"):
        source = REPO_ROOT / "static" / name
        if source.is_dir():
            shutil.copytree(source, DOCS / name, dirs_exist_ok=True)

    for script in POST_BUILD_SCRIPTS:
        run([sys.executable, script])

    if not (DOCS / "index.html").is_file():
        raise RuntimeError("Build failed: docs/index.html not found")
    print("=== Build complete ===")


if __name__ == "__main__":
    try:
        build()
    except RuntimeError as error:
        print(error, file=sys.stderr)
        sys.exit(1)
