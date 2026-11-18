# Data model

### D.1 — Page front matter

Each page in `content/` (not `_index.md`) starts with a TOML block between `+++` lines.

| Field | Required | Meaning |
|---|---|---|
| `title` | yes | Page title. |
| `path` | yes | Permanent URL path, for example `"/five-key-facts/"` (§C.2). |
| `updated` | yes | `YYYY-MM-DD`, written by `update_dates.py` (§I.4); never edited by hand. |
| `description` | no | Summary shown in lists and search. |
| `[taxonomies] categories` | yes | Slugs from the category vocabulary (§D.2). |
| `[taxonomies] tags` | yes | Free-form topic slugs; each becomes `/tags/<slug>/`. |
| `[extra] type` | yes | Document type shown as a label: `notes`, `resource`, `analysis`, `short-analysis`, or `response`. |
| `[extra] importance` | yes | Integer, default 5. Higher sorts earlier in "Featured" and on homepage cards; "Start Here" sorts ascending. |
| `[extra] featured` | yes | `true` lists the page under a category's "Featured" heading and first in its "Featured" sort. |
| `[extra] featuredimage` | no | Image path shown under the title. |

Leftover fields that templates ignore: top-level `categories` (3 pages), `[extra] doctype` (4), and
`[extra] maintopic` (3).

### D.2 — Category vocabulary

The 10 main categories are the keys of `[extra.categories]` in `config.toml`, each with a
one-sentence description. `[extra.category_names]` gives their display names, for example
`apologetics-responses = "Apologetics & Responses"`. Pages may also carry older category slugs
(for example `polygamy`), which still generate category pages but have no display name.

### D.3 — Search index

`docs/search_index.json`, written by `scripts/generate_search_index.py` after each build:
`{"pages": [{"title", "url", "snippet"}, …]}`. `templates/search.html` loads it in the browser.

### D.4 — Taxonomy index

`docs/taxonomy_index.json`, written by `scripts/generate_taxonomy_index.py` after each build:
`{"categories": [{"name", "count", "slug"}, …], "tags": [same]}`. Counts come from the built
site, so they are always current.

### D.5 — Static taxonomy lists

`static/data/categories.json` and `static/data/tags.json`, maintained by hand, each a list of
`{"name", "count", "slug"}`. The Browse page reads them. They are stale: in November 2026 they
listed 49 tags against 53 tag pages, and 110 Book of Mormon pages against 108 (§O.1).
