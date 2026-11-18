# Tasks

## Open

### T1 — Fix the taxonomy index pages

**Status:** to do
**Refs:** B6,V5

`/categories/` and `/tags/` each render a single broken link. Iterate `get_taxonomy(...).items` in
`templates/taxonomy_list.html`, show each term with its page count, and remove the two entries
from `KNOWN_BROKEN`.

### T2 — Fix the five broken content links

**Status:** to do
**Refs:** B7,V5

Repair or remove each target listed in §B.7, then remove the entries from `KNOWN_BROKEN`. Where a
target page was renamed, link to its current `path`; where a file is missing, restore it from git
history if it exists there.

### T3 — Give the untitled 1829-letter page a title

**Status:** to do
**Refs:** D1

`content/documents/book_of_mormon/translation/comparison_of_1829_letter_to_cowdery_and_bom_readability_metrics.md`
has no `title`, so it shows as an empty line in lists and sorts first under A–Z. Add a title and
make the hygiene of required fields (§D.1) a test.

### T4 — Remove the dead loaders from base.html

**Status:** to do
**Refs:** V6

`templates/base.html` fetches `taxonomy_index.json` on every page to fill tag clouds that no page
contains, and defines an unused Browse loader. Remove both.

### T5 — Make the release script safer

**Status:** to do
**Refs:** C3

Refuse to run unless the branch is `main`. Run `zola check --skip-external-links` and `pytest`
before committing. Stage untracked files with NUL-separated names so names with spaces work, and
limit them to `content/`, `static/`, and `docs/`. Print the non-`docs/` files being committed.

### T6 — Keep the Search page out of "Recently Updated"

**Status:** to do
**Refs:** V10

`content/search.md` is an ordinary page, so it appears in the homepage "Recently Updated" list.
Exclude it.

### T7 — Build the Browse lists from Zola's taxonomy

**Status:** to do
**Refs:** O1,D5,V6

Render the Browse lists at build time from `get_taxonomy`, so they include every term with current
counts and work without JavaScript (§C.4). Blocked by §O.1.

### T8 — Decide the resource title rule

**Status:** to do
**Refs:** O3

`templates/page.html` gives a larger, centered title to pages whose categories include
`resource`, but `resource` is a tag, so no page gets it. Blocked by §O.3.

### T9 — Remove leftover front matter fields

**Status:** to do
**Refs:** D1

Remove the top-level `categories`, `[extra] doctype`, and `[extra] maintopic` fields listed in
§D.1 after checking that no template reads them.

## Done
