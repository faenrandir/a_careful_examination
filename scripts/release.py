#!/usr/bin/env python3
"""
Release script for Zola-based site.

Switches to faenrandir user, builds the site with Zola,
commits changes, pushes, then switches back to jtprince.
"""

import subprocess
import sys
from datetime import datetime


RELEASE_USER = "faenrandir"
DEFAULT_USER = "jtprince"
HOSTNAME = "github.com"


def run(cmd: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command, printing it first."""
    print(f"  $ {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout.strip())
    if result.returncode != 0 and result.stderr:
        print(result.stderr.strip(), file=sys.stderr)
    if check and result.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}")
    return result


def switch_user(user: str):
    """Switch gh auth to the specified user."""
    run(f"gh auth switch --hostname {HOSTNAME} --user {user}")


def main():
    # Pre-flight: check zola is installed
    try:
        run("zola --version", check=True)
    except RuntimeError:
        print("ERROR: zola is not installed or not in PATH", file=sys.stderr)
        sys.exit(1)

    # Switch to release user
    switch_user(RELEASE_USER)

    try:
        # Pull latest changes
        run("git pull")

        # Update last-modified dates from git history
        run("python3 scripts/update_dates.py")

        # Clean build
        run("rm -rf docs")
        run("zola build")

        # Verify build succeeded
        import os
        if not os.path.isfile("docs/index.html"):
            raise RuntimeError("Build failed: docs/index.html not found")

        # Stage changes
        run("git add -u")
        run("git add $(git ls-files -o --exclude-standard)")

        # Check if there's anything to commit
        status = run("git status --porcelain", check=True)
        if not status.stdout.strip():
            print("No changes to commit.")
            return

        # Count changed files for commit message
        changed = len(status.stdout.strip().split("\n"))
        timestamp = datetime.now().strftime("%Y-%m-%d")
        message = f"Update site: {changed} file{'s' if changed != 1 else ''} changed ({timestamp})"

        run(f"git commit -m '{message}'")
        run("git push")

        print(f"\nDone. Committed and pushed: {message}")

    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        raise
    finally:
        # Always switch back
        switch_user(DEFAULT_USER)


if __name__ == "__main__":
    main()
