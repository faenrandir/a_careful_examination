#!/usr/bin/env python3
"""
Release script for Zola-based site.

Switches to faenrandir user, builds the site with Zola,
commits changes, pushes, then switches back to jtprince.

Use `--branch <name>` to run this against a non-main branch (e.g. an
experiment). In that mode the script:
  - refuses to operate unless the current branch matches `--branch`,
  - refuses to operate on `main`/`master` outright,
  - skips `git pull` when the branch has no upstream (typical for a
    freshly-created experiment branch), and
  - pushes with `--set-upstream` so a not-yet-existing remote branch
    is created and tracked.
The default (no `--branch`) path is unchanged and remains suitable for
the normal main-site release.
"""

import argparse
import os
import subprocess
import sys
from datetime import datetime


RELEASE_USER = "faenrandir"
DEFAULT_USER = "jtprince"
HOSTNAME = "github.com"
SAFE_BRANCHES_FORBIDDEN = {"main", "master"}


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


def current_branch() -> str:
    """Return the current git branch name."""
    result = run("git rev-parse --abbrev-ref HEAD", check=True)
    return result.stdout.strip()


def has_upstream() -> bool:
    """Return True if the current branch has a tracking (upstream) branch."""
    result = run("git rev-parse --abbrev-ref @{u} 2>/dev/null || true", check=False)
    return bool(result.stdout.strip())


def main():
    parser = argparse.ArgumentParser(
        description="Build, commit, and push the Zola site.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__)
    parser.add_argument("--branch",
                        help="Build & push to this branch (must be the current "
                             "branch; refuses main/master). Use for experiment/"
                             "feature branches so main is never touched. The "
                             "default path (no --branch) runs the normal release.")
    args = parser.parse_args()

    branch_mode = bool(args.branch)
    cb = current_branch()

    if branch_mode:
        if cb != args.branch:
            print(f"ERROR: --branch is '{args.branch}' but the current branch "
                  f"is '{cb}'. Switch to the target branch first.",
                  file=sys.stderr)
            sys.exit(1)
        if cb in SAFE_BRANCHES_FORBIDDEN:
            print(f"ERROR: refusing to run release on protected branch '{cb}'. "
                  "Releases to main must use the normal (no --branch) command.",
                  file=sys.stderr)
            sys.exit(1)
        print(f"Branch mode: building/pushing to '{cb}' (main is untouched).")

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
        if branch_mode:
            if has_upstream():
                run("git pull --ff-only")
            else:
                print("No upstream for this branch yet; skipping git pull.")
        else:
            run("git pull")

        # Update last-modified dates from git history
        run("python3 scripts/update_dates.py")

        # Clean build
        run("rm -rf docs")
        run("zola build")

        # Copy static assets to docs (fix broken images)
        run("cp -r static/documents docs/")
        run("cp -r static/images docs/ 2>/dev/null || true")

        # Fix absolute links in generated HTML
        run("python3 scripts/fix_links.py")

        # Generate search and taxonomy indices
        run("python3 scripts/generate_search_index.py")
        run("python3 scripts/generate_taxonomy_index.py")

        # Stage generated index files explicitly (they were deleted by rm -rf)
        run("git add docs/search_index.json docs/taxonomy_index.json")

        # Verify build succeeded
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

        if branch_mode:
            # Create/track the remote branch if needed, then push.
            run("git push --set-upstream origin HEAD")
        else:
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
