# Open questions

Decisions that only the maintainer can make. Retired so far — none.

### O1 — Are the static taxonomy lists still the canonical vocabulary?

The README calls `static/data/tags.json` the canonical tag list, but it is maintained by hand and
has fallen behind the site (§D.5). If it no longer needs to be canonical, Browse can be built from
Zola's own taxonomy (§T.7) and the two files can be deleted. If it does, something must keep it
current.

### O2 — Remove or replace the analytics tag?

`templates/base.html` loads Google Analytics with the Universal Analytics id `UA-125187615-1`.
Universal Analytics stopped processing data in July 2023, so the tag sends data nowhere. Remove it,
replace it with a GA4 property, or replace it with a different, lighter analytics service?

### O3 — Should resources get the larger, centered title?

The template intends a larger, centered title for resources but checks the categories instead of
the tags, so no page gets it (§T.8). Key it on the `resource` tag or the `type = "resource"`
field, or drop the special title?

### O4 — Delete the unused templates?

`templates/maintopic.html`, `templates/doctype.html`, and `templates/post.html` are not used by
any page. Delete them, or keep them for later use?
