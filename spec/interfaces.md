# Interfaces

### I.1 — scripts/build.py

`python3 scripts/build.py`, or `build()` when imported. Deletes `docs/`, runs `zola build`, copies
`static/documents` and `static/images` into `docs/`, then runs `fix_links.py`,
`generate_search_index.py`, and `generate_taxonomy_index.py`. Raises `RuntimeError` (exit 1 from
the command line) if a step fails or `docs/index.html` is missing. It never edits `content/`.

### I.2 — scripts/serve.py

`python3 scripts/serve.py` builds once, serves `docs/` at
`http://127.0.0.1:1111/a_careful_examination/`, and rebuilds when `content/`, `templates/`,
`sass/`, `static/`, `scripts/`, or `config.toml` change. Needs the `livereload` package and exits
with an install hint if it is missing.

### I.3 — scripts/release.py

`python3 scripts/release.py` publishes the site. It switches `gh` to the `faenrandir` account,
runs `git pull`, runs `update_dates.py`, builds (§I.1), stages every modified tracked file and
every untracked file, commits as `Update site: <n> files changed (<date>)`, pushes, and switches
`gh` back to `jtprince`. Uncommitted content edits are expected and are published with the
release.

### I.4 — scripts/update_dates.py

Run from the repository root. Writes each page's `updated` field (§D.1) from git history (§V.3)
and prints one line per changed file. A file with uncommitted text changes, or no history, gets
today's date.

### I.5 — URL scheme

Every URL starts with the base URL `/a_careful_examination`. A page lives at its front matter
`path`. Category pages live at `/categories/<slug>/` and topic pages at `/tags/<slug>/`. Other
fixed pages: `/`, `/about/`, `/recommended/`, `/browse/`, and `/search/` (which reads `?q=`).

### I.6 — Category page sort parameter

A category page accepts `?sort=featured` (default), `?sort=recent`, or `?sort=az`. The page script
reads it on load and rewrites it when a Sort link is clicked, so a sorted view can be shared (§V.7).
