#!/usr/bin/env python3
"""
Update 'updated' dates in content front matter based on git history.

For each .md file in content/, finds the last git commit date for the
corresponding original file and writes it into TOML front matter.
"""

import os
import re
import subprocess
import sys
from datetime import datetime


# Mapping from content paths back to original git repo paths.
# Most files kept their relative structure; these are the exceptions.
PATH_MAP = {
    "content/about/_index.md": "about.md",
    "content/recommended/_index.md": "recommended.md",
    "content/vetting-editorial.md": "vetting-editorial.md",
    "content/leaked/": "leaked/",
    "content/psychology_of_religion/": "psychology_of_religion/",
    "content/secular_humanism/": "secular_humanism/",
}

# The migration commit date — we find the last content change BEFORE this date.
MIGRATION_COMMIT = "fb4e0b1c"


def get_original_path(content_path: str) -> str:
    """Map a content/ file path back to its original git repo path."""
    # Direct mappings
    if content_path in PATH_MAP:
        return PATH_MAP[content_path]

    # Prefix mappings (directories)
    for prefix, orig_prefix in PATH_MAP.items():
        if prefix.endswith("/"):
            if content_path.startswith(prefix):
                return orig_prefix + content_path[len(prefix):]

    # Default: strip content/ prefix
    if content_path.startswith("content/"):
        return content_path[len("content/"):]

    return content_path


def get_last_commit_date(filepath: str) -> str | None:
    """Get the last commit date for a file in YYYY-MM-DD format.
    Finds the last change BEFORE the migration commit."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ci", "--before", MIGRATION_COMMIT, "--", filepath],
            capture_output=True, text=True, check=True
        )
        if not result.stdout.strip():
            return None
        # Parse: "2026-04-04 15:00:00 -0600"
        date_str = result.stdout.strip().split()[0]
        return date_str
    except subprocess.CalledProcessError:
        return None


def update_front_matter(filepath: str, date: str) -> bool:
    """Add or update the 'updated' field in TOML front matter.
    Returns True if the file was modified."""
    content = open(filepath).read()

    # Match TOML front matter
    fm_match = re.match(r'^\+\+\+\n(.*?)\n\+\+\+', content, re.DOTALL)
    if not fm_match:
        # No front matter at all - add it
        new_content = f'+++\nupdated = "{date}"\n+++\n\n' + content.lstrip()
        open(filepath, "w").write(new_content)
        return True

    fm_content = fm_match.group(1)

    # Check if updated date already exists and matches
    existing_match = re.search(r'^updated = "([^"]+)"', fm_content, re.MULTILINE)
    if existing_match and existing_match.group(1) == date:
        return False  # Already up to date

    if existing_match:
        # Update existing
        new_fm = re.sub(
            r'^updated = "[^"]+"',
            f'updated = "{date}"',
            fm_content,
            flags=re.MULTILINE
        )
    else:
        # Add new field
        if fm_content.strip():
            new_fm = fm_content.rstrip() + f'\nupdated = "{date}"\n'
        else:
            # Empty front matter
            new_fm = f'updated = "{date}"\n'

    new_content = content.replace(fm_content, new_fm, 1)
    open(filepath, "w").write(new_content)
    return True


def main():
    content_dir = "content"
    updated_count = 0
    skipped_count = 0
    error_count = 0

    for root, dirs, files in os.walk(content_dir):
        for filename in files:
            if not filename.endswith(".md"):
                continue

            filepath = os.path.join(root, filename)
            rel_path = filepath  # Already relative to repo root

            # Skip _index.md files (sections don't display updated dates)
            if filename == "_index.md":
                skipped_count += 1
                continue

            orig_path = get_original_path(rel_path)
            date = get_last_commit_date(orig_path)

            if date is None:
                # File has no git history (new file)
                date = datetime.now().strftime("%Y-%m-%d")

            if update_front_matter(filepath, date):
                updated_count += 1
                print(f"  Updated: {filepath} -> {date}")
            else:
                skipped_count += 1

    print(f"\nDone. Updated: {updated_count}, Skipped (unchanged): {skipped_count}, Errors: {error_count}")


if __name__ == "__main__":
    main()
