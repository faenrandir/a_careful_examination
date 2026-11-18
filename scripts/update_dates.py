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

# The Jekyll-to-Zola migration commit (file moves, not content changes).
MIGRATION_COMMIT = "fb4e0b1c"

# Bulk commits that rewrote paths mechanically in many files without changing
# what the articles say. They never count as an update.
MECHANICAL_COMMITS = (
    MIGRATION_COMMIT,
    "4fd5ab99",  # 2026-04-04 fix quoting in link shortcodes after the migration
    "1654c904",  # 2026-08-25 add /a_careful_examination prefix to media paths
    "edab4be3",  # 2019-01-10 make many internal links relative
    "e5e3f65a",  # 2026-08-23 convert {{ link() }} and {{ img() }} shortcodes for new Zola
)

# Leading front matter: TOML (+++) now, YAML (---) before the Zola migration.
_FRONT_MATTER = re.compile(r"^\s*(\+\+\+|---)\n.*?\n\1[ \t]*(\n|$)", re.DOTALL)

# Zola link shortcode, replaced by plain Markdown links in e5e3f65a (2026-08-23).
# Normalized as well in case a later commit finished converting a file.
_LINK_SHORTCODE = re.compile(
    r'\{\{\s*link\(\s*text\s*=\s*"((?:[^"\\]|\\.)*)"\s*,\s*path\s*=\s*"([^"]*)"\s*\)\s*\}\}'
)


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


def _body(text: str) -> str:
    """Return the article text in a form that changes only when the article
    itself changes.

    Front matter is dropped, so re-tagging or re-categorizing a page is not an
    update. Two bulk mechanical rewrites are undone so they do not count either:
    the `{{ link() }}` shortcode conversion and the lds.org ->
    churchofjesuschrist.org domain swap. Blank lines and trailing whitespace are
    ignored.
    """
    text = _FRONT_MATTER.sub("", text, count=1)
    text = _LINK_SHORTCODE.sub(r"[\1](\2)", text)
    text = text.replace("churchofjesuschrist.org", "lds.org")
    return "\n".join(line.rstrip() for line in text.splitlines() if line.strip())


def _file_at(commit_hash: str, *paths: str) -> str | None:
    """File contents at a commit, trying each path in turn; None if absent."""
    for path in paths:
        result = subprocess.run(
            ["git", "show", f"{commit_hash}:{path}"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            return result.stdout
    return None


def get_last_commit_date(orig_path: str, content_path: str) -> str | None:
    """Date (YYYY-MM-DD) of the most recent commit that changed the article text.

    Walks the file's history across both the original (pre-migration) path and
    the current content path, newest first, and compares each version's body
    with the version before it. Commits that changed only front matter, and the
    commits in MECHANICAL_COMMITS, are skipped.
    """
    try:
        result = subprocess.run(
            ["git", "log", "--format=%H %cs", "--", orig_path, content_path],
            capture_output=True, text=True, check=True
        )
    except subprocess.CalledProcessError:
        return None

    versions = []  # (hash, date, body or None), newest first
    for line in result.stdout.split("\n"):
        if not line.strip():
            continue
        commit_hash, commit_date = line.split()[:2]
        text = _file_at(commit_hash, content_path, orig_path)
        versions.append((commit_hash, commit_date, None if text is None else _body(text)))

    for i, (commit_hash, commit_date, body) in enumerate(versions):
        if body is None or commit_hash.startswith(MECHANICAL_COMMITS):
            continue
        previous = next((v[2] for v in versions[i + 1:] if v[2] is not None), None)
        if previous is None or previous != body:
            return commit_date
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

    # Only manage the top-level `updated` field (before any [table] header,
    # e.g. [extra]). An `updated` inside a table is not page.updated and must
    # not be mistaken for it.
    top_level, separator, table_part = fm_content.partition("\n[")
    if separator:
        table_part = "[" + table_part

    # Check if updated date already exists and matches
    existing_match = re.search(r'^updated = "([^"]+)"', top_level, re.MULTILINE)
    if existing_match and existing_match.group(1) == date:
        return False  # Already up to date

    if existing_match:
        # Update existing
        new_top = re.sub(
            r'^updated = "[^"]+"',
            f'updated = "{date}"',
            top_level,
            flags=re.MULTILINE
        )
    else:
        # Add new field at top level
        if top_level.strip():
            new_top = top_level.rstrip() + f'\nupdated = "{date}"\n'
        else:
            # Empty front matter
            new_top = f'updated = "{date}"\n'

    # Reassemble without adding or removing surrounding blank lines, so
    # repeated runs leave the rest of the front matter byte-for-byte unchanged.
    new_fm = new_top + ("\n" + table_part if table_part else "")
    new_content = content.replace(fm_content, new_fm, 1)
    open(filepath, "w").write(new_content)
    return True


def has_uncommitted_changes(filepath: str) -> bool:
    """True if the working copy's article text differs from HEAD.

    Front-matter-only edits (including this script's own `updated` line) do not
    count. Untracked files count as changed.
    """
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain", "--", filepath],
            capture_output=True, text=True, check=True
        )
    except subprocess.CalledProcessError:
        return False
    status_line = result.stdout.strip()
    if not status_line:
        return False
    if status_line.startswith("??"):
        return True
    head_text = _file_at("HEAD", filepath)
    if head_text is None:
        return True
    with open(filepath) as f:
        return _body(f.read()) != _body(head_text)


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

            # If the file has uncommitted changes it was just edited; that edit
            # is what this release will commit, so stamp today's date.
            if has_uncommitted_changes(rel_path):
                date = datetime.now().strftime("%Y-%m-%d")
            else:
                date = get_last_commit_date(orig_path, rel_path)

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
