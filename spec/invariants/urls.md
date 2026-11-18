# URL and navigation invariants

Covers published URLs (§C.2), the Browse page, and category pages.

### V5 — Every internal link in the built site resolves

Every `href` or `src` in the built HTML that starts with `/a_careful_examination/` resolves to a
file in `docs/`. The only exceptions are listed in `KNOWN_BROKEN` in the test, each naming an open
bug. An exception that starts resolving fails the test until it is removed from the list, so the
list only shrinks.

Test: tests/test_urls.py::test_every_internal_link_resolves

### V6 — Browse links point at the taxonomy they list

Every entry on the Browse page links to a generated page: categories under
`/categories/<slug>/` and topics under `/tags/<slug>/`.

Test: tests/test_urls.py::test_browse_entries_link_to_generated_pages

### V7 — Category pages can be re-sorted in the browser

Every item in a category page's full resource list carries `data-updated`, `data-importance`, and
`data-featured`, and the page's script reorders the list for `?sort=featured`, `?sort=recent`,
and `?sort=az`. The build cannot read the query string, so sorting must happen in the browser.

Test: tests/test_urls.py::test_category_items_carry_sort_keys
