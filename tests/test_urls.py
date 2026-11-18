"""Internal links, the Browse page, and category sorting (spec/invariants/urls.md)."""

import json
import re
from pathlib import Path
from urllib.parse import unquote

BASE = "/a_careful_examination"

#: Internal targets known to be broken, each with the open bug that tracks it. Remove an entry
#: when its target is fixed; the test fails until you do, so this list only shrinks.
KNOWN_BROKEN = {
    f"{BASE}/influences-on-word-of-wisdom/": "§B.7",
    f"{BASE}/health-studies-on-coffee/pubmed": "§B.7",
    f"{BASE}/critique-of-price-analysis-on-brotherton/(https://www.millennialstar.org/who-was-john-mcilwrick/)": "§B.7",
    f"{BASE}/documents/polygamy/denials/Millenial-Star-04-n9-Editorials-pg143-144.pdf": "§B.7",
    f"{BASE}/contemporary-evidence-that-joseph-smith-practiced-polygamy/media/dc132-color-coded-by-expositor-affidavits.png": "§B.7",
}


def _resolves(site: Path, url: str) -> bool:
    path = site / unquote(url)[len(BASE) + 1:]
    return (path / "index.html").is_file() if url.endswith("/") else path.exists()


def test_every_internal_link_resolves(site):
    """§V.5: every /a_careful_examination/ href or src in the built HTML resolves."""
    broken: dict[str, str] = {}
    for page in site.rglob("*.html"):
        html = page.read_text(encoding="utf-8", errors="replace")
        for url in re.findall(rf'(?:href|src)="({BASE}/[^"#?]*)', html):
            if not _resolves(site, url):
                broken.setdefault(url, str(page.relative_to(site)))

    new = {url: where for url, where in broken.items() if url not in KNOWN_BROKEN}
    assert not new, f"broken internal links (target <- page): {new}"
    fixed = sorted(set(KNOWN_BROKEN) - set(broken))
    assert not fixed, f"these KNOWN_BROKEN targets now resolve; remove them from the list: {fixed}"


def test_browse_entries_link_to_generated_pages(site):
    """§V.6: Browse links categories under /categories/ and topics under /tags/ (§B.1)."""
    html = (site / "browse" / "index.html").read_text(encoding="utf-8")
    calls = dict(re.findall(r"renderTaxonomy\(\w+, '([\w-]+)', '(\w+)'\)", html))
    assert calls == {"categories-list": "categories", "tags-list": "tags"}, (
        f"Browse renders lists with the wrong URL sections: {calls}"
    )
    assert "base + '/' + section + '/'" in html, "Browse links are not built from the section"

    for data_file, section in (("categories.json", "categories"), ("tags.json", "tags")):
        terms = json.loads((site / "data" / data_file).read_text(encoding="utf-8"))
        missing = [t["slug"] for t in terms if not (site / section / t["slug"] / "index.html").is_file()]
        assert not missing, f"Browse lists {section} with no generated page: {missing}"


def test_category_items_carry_sort_keys(site):
    """§V.7: every category list item has sort keys, and the script handles all three sorts (§B.5)."""
    pages = sorted((site / "categories").glob("*/index.html"))
    assert pages, "no category pages were built"
    for page in pages:
        html = page.read_text(encoding="utf-8")
        match = re.search(r'<ul class="resource-list" id="all-resources-list">(.*?)</ul>', html, re.S)
        assert match, f"{page.parent.name}: no #all-resources-list"
        items = re.findall(r"<li class=\"resource-item\"(.*?)>", match.group(1), re.S)
        assert items, f"{page.parent.name}: empty resource list"
        for attrs in items:
            for key in ("data-updated", "data-importance", "data-featured"):
                assert key in attrs, f"{page.parent.name}: an item lacks {key}"
        for mode in ("featured:", "recent:", "az:"):
            assert mode in html, f"{page.parent.name}: the sort script has no {mode[:-1]} order"
        assert "searchParams.get('sort')" in html or "get('sort')" in html
