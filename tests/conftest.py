"""Shared fixtures. Tests that read the built site request `site`, which rebuilds docs/ once per
session through scripts/build.py, exactly as the preview and the release do (§V.2)."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))


@pytest.fixture(scope="session")
def site() -> Path:
    """Build the site once and return the docs/ directory."""
    import build

    build.build()
    return build.DOCS
