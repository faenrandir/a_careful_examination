# Bug log

### B1 — Browse topic links pointed at /categories/

**Date:** 2026-11-18 · **Status:** fixed · **Caught by:** V6

The Browse page script built every link as `/categories/<slug>/`, including topics, so every topic
link returned 404 on the live site. Rule: when one function renders more than one taxonomy, pass
the URL section in explicitly.

### B2 — Page dates came from front-matter-only commits

**Date:** 2026-11-18 · **Status:** fixed · **Caught by:** V3

`update_dates.py` counted any changed line other than `updated` as a content change. One
re-categorization commit edited the front matter of 430 pages, so 416 of 431 pages showed the same
date. Rule: compare article text, not raw diffs, and treat bulk mechanical rewrites as no change.

### B3 — update_dates.py added a blank line on every rewrite

**Date:** 2026-11-18 · **Status:** fixed · **Caught by:** V4

Reassembling the front matter appended a newline after a part that already ended in one, so each
date change also grew the front matter by a blank line. Rule: rewrite one field in place; never
rebuild the surrounding text.

### B4 — Homepage "Recently Updated" listed the oldest pages first

**Date:** 2026-11-18 · **Status:** fixed · **Caught by:** V10

The template passed `reverse=true` to Tera's `sort`, which ignores it. While every page shared one
date the mistake was invisible. Rule: reverse with the `reverse` filter, and test orderings on data
with distinct keys.

### B5 — Category sort links did nothing

**Date:** 2026-11-18 · **Status:** fixed · **Caught by:** V7

The category template branched on a `sort` variable taken from the query string, which a static
build never sees, so every visitor got one order. Rule: anything that depends on the request must
run in the browser.

### B6 — Taxonomy index pages link to /categories/categories/ and /tags/tags/

**Date:** 2026-11-18 · **Status:** open · **Caught by:** V5

`templates/taxonomy_list.html` iterates over the object that `get_taxonomy` returns as if it were
a list of terms, so it renders one link built from the taxonomy's own name. Rule: iterate
`get_taxonomy(...).items`. Fix with §T.1.

### B7 — Five content pages link to missing internal targets

**Date:** 2026-11-18 · **Status:** open · **Caught by:** V5

The built site links to `/influences-on-word-of-wisdom/` (from recommended),
`/health-studies-on-coffee/pubmed`, a Markdown URL wrapped in an internal path on
`critique-of-price-analysis-on-brotherton`, a missing Millennial Star PDF under
`/documents/polygamy/denials/`, and an image under
`/contemporary-evidence-that-joseph-smith-practiced-polygamy/media/`. Rule: link checks must run
on the built HTML, not only on Markdown. Fix with §T.2.

### B8 — The preview lost its styles after the first rebuild

**Date:** 2026-11-18 · **Status:** fixed · **Caught by:** V2

`serve.py` served `docs/` through `docs/a_careful_examination/`, a folder of symlinks that each
rebuild's removal of `docs/` deleted, so CSS and pages returned 404 after the first edit. It also
had its own copy of the build steps. Rule: the preview builds through `build.py` and maps the base
URL onto `docs/` without writing into it.
