"""Build pipeline, preview server, and page dates (spec/invariants/build.md)."""

import re
from pathlib import Path

import build
import serve
import update_dates

SCRIPTS = Path(build.__file__).resolve().parent


def test_build_produces_pages_indexes_and_documents(site):
    """§V.1: a build yields the pages, both JSON indexes, and docs/documents/."""
    for name in ("index.html", "search_index.json", "taxonomy_index.json"):
        assert (site / name).is_file(), f"docs/{name} missing after build"
    assert (site / "documents").is_dir(), "docs/documents/ missing after build"


def test_serve_and_release_build_through_build_py(site):
    """§V.2: serve.py and release.py build only via build.py, and the preview serves docs/
    without writing into it (§B.8)."""
    for script in ("serve.py", "release.py"):
        source = (SCRIPTS / script).read_text(encoding="utf-8")
        assert re.search(r"^from build import .*\bbuild\b", source, re.M), (
            f"{script} does not import build() from build.py"
        )
        for step in ["zola build", *build.POST_BUILD_SCRIPTS]:
            assert step not in source, f"{script} runs {step!r} itself instead of build()"

    def get(path):
        status = {}
        body = b"".join(serve.site_app(
            {"PATH_INFO": path}, lambda s, h: status.setdefault("code", s.split()[0])))
        return status["code"], body

    assert get("/a_careful_examination/main.css")[0] == "200"
    assert get("/a_careful_examination/tags/analogy/")[0] == "200"
    assert get("/a_careful_examination/../config.toml")[0] == "404"
    assert not (site / "a_careful_examination").exists(), "the preview wrote into docs/"


def test_body_ignores_front_matter_and_mechanical_rewrites():
    """§V.3: only article-text edits change a page's date (§B.2)."""
    page = '+++\ntitle = "A"\nupdated = "2020-01-01"\n[taxonomies]\ntags = ["x"]\n+++\n\nText [here](https://www.churchofjesuschrist.org/a).\n'
    retagged = page.replace('tags = ["x"]', 'tags = ["x", "y"]').replace("2020-01-01", "2026-09-30")
    old_domain = page.replace("churchofjesuschrist.org", "lds.org")
    jekyll = '---\ntitle: "A"\n---\n\nText [here](https://www.lds.org/a).\n'
    body = update_dates._body(page)
    assert update_dates._body(retagged) == body
    assert update_dates._body(old_domain) == body
    assert update_dates._body(jekyll) == body

    shortcode = '{{ link(text="Five Key Facts", path="/five-key-facts/") }}'
    assert update_dates._body(shortcode) == update_dates._body("[Five Key Facts](/five-key-facts/)")

    assert update_dates._body(page.replace("Text", "Revised text")) != body
    assert update_dates.MIGRATION_COMMIT in update_dates.MECHANICAL_COMMITS


def test_update_front_matter_changes_only_the_updated_line(tmp_path):
    """§V.4: restamping rewrites only the updated line, and repeating it is a no-op (§B.3)."""
    original = (
        '+++\ntitle = "A"\npath = "/a/"\nupdated = "2020-01-01"\n[taxonomies]\n'
        'tags = ["x"]\n\n[extra]\nimportance = 5\n\n+++\n\nBody.\n'
    )
    page = tmp_path / "page.md"
    page.write_text(original)

    assert update_dates.update_front_matter(str(page), "2024-05-06")
    assert page.read_text() == original.replace("2020-01-01", "2024-05-06")
    assert not update_dates.update_front_matter(str(page), "2024-05-06")
    assert page.read_text() == original.replace("2020-01-01", "2024-05-06")
