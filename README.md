# A Careful Examination: researching LDS truth-claims and thinking

See [About](https://faenrandir.github.io/a_careful_examination/about/).

The site is built with [Zola](https://www.getzola.org/) 0.23 and published by GitHub Pages from
the `docs/` folder on `main`. `docs/` is generated output; do not edit it by hand.

## Working on the site

Run every command from the repository root. Zola must be installed and on your `PATH`.

Preview the site with live reload:

    python3 scripts/serve.py

The preview opens at <http://127.0.0.1:1111/a_careful_examination/> and rebuilds when content,
templates, styles, static files, scripts, or `config.toml` change. It needs the `livereload`
package (`pip install livereload`).

Publish the site:

    python3 scripts/release.py

The release script switches the GitHub CLI to the `faenrandir` account, pulls, updates page dates,
builds, commits every change (including uncommitted content edits) as `Update site: <n> files
changed (<date>)`, pushes, and switches back to `jtprince`.

Other commands:

| Command | Purpose |
|---|---|
| `python3 scripts/build.py` | Build `docs/` once without serving or publishing. The preview and the release use the same build. |
| `pytest` | Run the tests. They rebuild `docs/` once and check links, ordering, styles, and the specification's format. |
| `python3 scripts/update_dates.py` | Rewrite each page's `updated` date from git history. The release runs it automatically. |

Running `zola serve` or `zola build` directly skips the post-build steps (link fixes, the search
index, and the taxonomy index), so search and some links do not work in that output.

## Specification

The rules the site must keep are written down and tested:

- `AGENTS.md` states the goal, the fixed constraints, and the rules for changing the code.
- `SPEC.md` indexes the specification in `spec/`: invariants, the data model, interfaces, open
  tasks, open questions, and the bug log.
- `FORMAT.md` defines the entry formats, which `tests/test_spec_hygiene.py` checks.

Narrative notes belong in `notes/`, because `docs/` is the generated site.

## Site organization

### Taxonomy

- **Categories**: the 10 categories in `[extra.categories]` in `config.toml`, with display names
  in `[extra.category_names]`.
- **Tags** (shown as "Topics"): free-form, taken from each page's front matter. Every tag gets a
  page at `/tags/<slug>/`.

Front matter fields are described in `spec/data-model.md` (§D.1).

### Homepage

`templates/index.html` renders three sections:

- **Start Here** lists pages tagged `start-here`. The "peek behind the curtain" article
  (`path = "/to-peek-behind-the-curtain/"`) comes first, then the rest in ascending
  `extra.importance`.
- **Browse the Collection** shows one card per category with its description and its 5 pages of
  highest `extra.importance`.
- **Recently Updated** lists the 8 most recently updated pages, newest first.

### Browse page (`/browse/`)

`templates/browse.html` lists categories and topics in the browser from
`static/data/categories.json` and `static/data/tags.json`. These files are maintained by hand and
are currently out of date (§D.5, §O.1).

### Category pages (`/categories/<slug>/`)

`templates/categories/single.html` shows a "Featured" list (pages with `extra.featured = true`)
and a full list that the reader can sort by Featured, Recently Updated, or A–Z. Sorting runs in
the browser, and the choice is kept in the URL as `?sort=featured|recent|az`.

### Topic pages (`/tags/<slug>/`)

`templates/taxonomy_single.html` lists every page with that tag.

### Page dates

Each page's `updated` date is the date of the last commit that changed its article text.
Changes to front matter alone (categories, tags, importance, title) do not change the date
(§V.3).

## License

Code is under the MIT license, and all content produced by faenrandir is under a CC0 license.
The copyright to copies of content produced by others is held by them. See LICENSE for details.
