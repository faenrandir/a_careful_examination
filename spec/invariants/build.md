# Build and release invariants

Covers `scripts/`: the build pipeline, the preview server, the release script, and the page
dates that `update_dates.py` writes.

### V1 — A build produces the pages, both indexes, and the documents folder

After `scripts/build.py` runs, `docs/` contains `index.html`, `search_index.json`,
`taxonomy_index.json`, and the `documents/` folder copied from `static/documents/`.

Test: tests/test_build.py::test_build_produces_pages_indexes_and_documents

### V2 — The preview and the release use the one build pipeline

`scripts/serve.py` and `scripts/release.py` build only by calling `build()` from
`scripts/build.py`. Neither runs `zola build` or a post-build script itself, so the preview and
the published site cannot drift apart. The preview serves `docs/` without writing anything inside
it.

Test: tests/test_build.py::test_serve_and_release_build_through_build_py

### V3 — A page's date changes only when its article text changes

`update_dates.py` dates a page by the last commit that changed its article text. Edits to front
matter alone (categories, tags, importance, title) do not count. Neither do the two bulk
mechanical rewrites: the `lds.org` to `churchofjesuschrist.org` domain swap and the conversion of
`{{ link() }}` shortcodes to Markdown links. Commits listed in `MECHANICAL_COMMITS` never count.

Test: tests/test_build.py::test_body_ignores_front_matter_and_mechanical_rewrites

### V4 — Restamping a date changes only the updated line

When `update_dates.py` rewrites a page's date, the only bytes that change are those of the
top-level `updated = "YYYY-MM-DD"` line, and writing the same date again changes nothing.

Test: tests/test_build.py::test_update_front_matter_changes_only_the_updated_line
