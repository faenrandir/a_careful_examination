# Presentation invariants

Covers `sass/` and the templates that decide what a reader sees.

### V8 — Colors come only from the token file

No file in `sass/` other than `_tokens.scss` contains a hex color literal, and no file uses CSS
custom properties (`var(--…)`). This keeps every color in one place (§C.5).

Test: tests/test_presentation.py::test_colors_only_in_tokens

### V9 — Article lists sit 40px inside paragraph text

In the compiled CSS, the left margin of `.post-content ul` and `.post-content ol` is 40px larger
than the left margin of `.post-content p`, so lists are easy to tell apart from paragraphs.

Test: tests/test_presentation.py::test_lists_indent_past_paragraphs

### V10 — The homepage lists recently updated pages newest first

The dates in the homepage "Recently Updated" list are in descending order.

Test: tests/test_presentation.py::test_homepage_recent_is_newest_first

### V11 — An article page shows one updated date

An article page that has an `updated` date shows it exactly once, in the metadata row.

Test: tests/test_presentation.py::test_article_shows_one_updated_date

### V12 — Muted text and the accent are readable on the page background

`$ink-muted` and `$accent` each have a contrast ratio of at least 4.5:1 against `$paper`, the
WCAG AA minimum for body text.

Test: tests/test_presentation.py::test_text_colors_meet_contrast_minimum
