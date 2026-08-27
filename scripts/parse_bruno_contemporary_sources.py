#!/usr/bin/env python3
"""Parse Cheryl L. Bruno's "Contemporary Sources for JS Polygamy" docx chart.

The source document is a single large Word table (with one row of per-cell
column headers and a row of full-width section headers) shared by Cheryl L.
Bruno in a Facebook post (Aug 22, 3:34 PM MT) to the "Mormon Polygamy
Documents" Facebook group.  The table is split into logical sections by the
full-width header rows.

This script extracts that table, splits it into its constituent sections, and
writes a Markdown file (one `## ` section per split, each with its own table)
suitable for inclusion in the "A Careful Examination" Zola site.

Only the Python standard library is used (docx files are zip archives of XML).
"""

from __future__ import annotations

import datetime
import re
import sys
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

# recognizes docx_link and script_link
INTRODUCTION = """
Cheryl L. Bruno has shared her ongoing documentary catalog in the Mormon Polygamy 
Documents Facebook group detailing contemporary sources on Joseph Smith's practice of polygamy. 
Her work revises and expands upon Mark Tensmeyer’s work published in 
"Secret Covenants: New Insights on Early Mormon Polygamy."

**Source document:** {docx_link} (original `.docx` from Bruno's Facebook post)

Below is the table programmatically extracted from her document with this script: {script_link}.
Edits to the md/html docs will be overwritten when the script is rerun, so modify the script to 
change this document. As she releases new updates, I update this document.

```
CCLA – Community of Christ Library and Archives
CHL – Church History Library
JSP – Joseph Smith Papers
WWP – Wilford Woodruff Papers
```
"""

# A full-width header row spans all four columns; these divide the single mega
# table into its logical sub-tables.
HEADER_COL_COUNT = 4

# --- Output / source locations (kept in sync across the generated page) -------
REPO = "faenrandir/a_careful_examination"
BRANCH = "main"
DOCX_FILENAME = "Contemporary_Sources_for_JS_Polygamy_(chart)_8.22.26.docx"
DOCX_STATIC_PATH = f"/media/{DOCX_FILENAME}"
# base_url from config.toml; mirrors what Zola's `get_url(path=DOCX_STATIC_PATH)`
# would produce, so these plain links render identically to `{{ link(...) }}`.
BASE_URL = "/a_careful_examination"
PAGE_URL = f"{BASE_URL}/bruno-contemporary-sources-for-js-polygamy/"
SCRIPT_PATH = "scripts/parse_bruno_contemporary_sources.py"
SCRIPT_URL = f"https://github.com/{REPO}/blob/{BRANCH}/{SCRIPT_PATH}"
DOCX_LINK_URL = f"{BASE_URL}{DOCX_STATIC_PATH}"


# Scoped layout CSS emitted into the generated Bruno page only (see
# render_markdown). The <style> block lives in this one generated page, so the
# rules apply solely to its tables: widen the reading column a bit and split the
# columns into the Date:Source:Location:Notes ratio (~1.8:2.5:3:4) using a fixed
# layout, so the first two columns stop dominating and the table fills its width.
TABLE_STYLES = """<style>
.page-content .wrapper { max-width: min(1000px, 100vw); }
table { width: 100%; max-width: 100%; table-layout: fixed; }
table td, table th { vertical-align: top; word-wrap: anywhere; }
table th:nth-child(1), table td:nth-child(1) { width: 16%; }
table th:nth-child(2), table td:nth-child(2) { width: 22%; }
table th:nth-child(3), table td:nth-child(3) { width: 27%; }
table th:nth-child(4), table td:nth-child(4) { width: 35%; }
</style>"""


def _local(tag: str) -> str:
    """Return the local part of a Clark-notation XML tag."""
    return tag.split("}", 1)[-1]


def _rel_id(elem: ET.Element) -> str | None:
    """Return the relationship id referenced by a ``w:hyperlink`` element.

    The ``r:id`` attribute lives in a relationships namespace; the exact
    namespace URI differs between producers, so we match by local name.
    """
    for key, value in elem.attrib.items():
        if _local(key) == "id":
            return value
    return None


def _text_of(elem: ET.Element) -> str:
    """Return the concatenated text of every ``w:t`` descendant."""
    return "".join(t.text or "" for t in elem.iter(f"{{{NS['w']}}}t"))


def load_rels(root: ET.Element) -> dict[str, str]:
    """Map relationship Id -> target URL for external hyperlink relationships.

    The ``Relationship`` elements live in the package relationships namespace
    while each carries unprefixed ``Id``/``Target``/``TargetMode`` attributes.
    We match by local tag name for namespace-agnostic robustness.
    """
    rels: dict[str, str] = {}
    for rel in root.iter():
        if _local(rel.tag) == "Relationship":
            if rel.get("TargetMode") == "External":
                rels[rel.get("Id", "")] = rel.get("Target", "")
    return rels


def collect_fragments(elem: ET.Element, rels: dict[str, str]) -> list[tuple]:
    """Walk *elem* in document order collecting text and hyperlink spans.

    Each returned tuple is either ``("text", str)`` or ``("link", text, url)``
    so that surrounding text can be interleaved with links exactly as authored.
    """
    frags: list[tuple] = []
    for child in elem:
        tag = _local(child.tag)
        if tag == "t":
            frags.append(("text", child.text or ""))
        elif tag == "hyperlink":
            rid = _rel_id(child)
            url = rels.get(rid, "") if rid else ""
            inner = collect_fragments(child, rels)
            inner_text = "".join(part for _, part, *_ in inner)
            frags.append(("link", inner_text, url))
        else:
            # Runs, paragraphs, ... may contain w:t / w:hyperlink children.
            frags.extend(collect_fragments(child, rels))
    return frags


def render_fragments(frags: list[tuple]) -> str:
    """Render collected fragments into Markdown inline text."""
    out: list[str] = []
    for frag in frags:
        kind = frag[0]
        if kind == "text":
            out.append(frag[1])
        else:  # ("link", text, url)
            _kind, text, url = frag
            if url and text:
                out.append(f"[{text}](<{url}>)")
            else:
                out.append(text)
    return "".join(out)


def render_cell(text: str) -> str:
    """Escape text for safe use inside a Markdown table cell."""
    # Collapse line wrapping / manual breaks into single spaces.
    text = text.replace("\r\n", " ").replace("\r", " ").replace("\n", " ")
    text = re.sub(r"[ \t]+", " ", text).strip()
    # Escape backslashes first, then pipes (which would break the table).
    text = text.replace("\\", "\\\\").replace("|", "\\|")
    return text


def slugify(text: str) -> str:
    """Match Zola's default heading-id slugification.

    Zola lowercases the heading, then replaces every run of non-alphanumeric
    characters (whitespace, punctuation, symbols) with a single hyphen and
    collapses/strips surplus hyphens.  We replicate that exactly so generated
    TOC anchors line up with Zola's auto-generated heading ids.
    """
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


def row_cells(row: ET.Element, rels: dict[str, str]) -> list[str]:
    cells = row.findall(f"{{{NS['w']}}}tc", NS)
    out = []
    for cell in cells:
        frags = collect_fragments(cell, rels)
        out.append(render_fragments(frags))
    return out


def is_full_width_header(row: ET.Element) -> bool:
    cells = row.findall(f"{{{NS['w']}}}tc", NS)
    if len(cells) != 1:
        return False
    gridspan = cells[0].find(f".//{{{NS['w']}}}gridSpan", NS)
    if gridspan is None:
        return False
    val = gridspan.get(f"{{{NS['w']}}}val")
    return val == str(HEADER_COL_COUNT)


def parse_table(docx_path: Path):
    """Return a list of sections: each is (title, [row-text-lists])."""
    with zipfile.ZipFile(docx_path) as zf:
        doc_xml = zf.read("word/document.xml")
        rels_xml = zf.read("word/_rels/document.xml.rels")

    root = ET.fromstring(doc_xml)
    rels_root = ET.fromstring(rels_xml)
    rels = load_rels(rels_root)

    tbl = root.find(f".//{{{NS['w']}}}tbl", NS)
    if tbl is None:
        raise SystemExit("No table found in document.xml")

    rows = tbl.findall(f".//{{{NS['w']}}}tr", NS)

    sections: list[tuple[str, list[list[str]]]] = []
    current_title: str | None = None
    current_rows: list[list[str]] = []
    seen_header = False
    in_title_section = False

    def cells_of(row):
        return row_cells(row, rels)

    for row in rows:
        cells = cells_of(row)
        if is_full_width_header(row):
            # A full-width header row begins a new section.
            if current_title is not None or in_title_section:
                sections.append((current_title or "", current_rows))
            title = _text_of(row).strip()
            current_title = title
            current_rows = []
            in_title_section = True
            seen_header = False
            continue

        if not seen_header and cells == ["Date", "Source", "Location", "Notes"]:
            # The column-header row for the first ("explicit sources") section.
            seen_header = True
            continue

        if cells and any(c.strip() for c in cells):
            current_rows.append(cells)

    if current_title is not None:
        sections.append((current_title, current_rows))

    return sections


COLUMNS = ["Date", "Source", "Location", "Notes"]


def render_markdown(sections: list[tuple[str, list[list[str]]]]) -> str:
    lines: list[str] = []
    lines.append(_front_matter())
    lines.append("")
    lines.append(_provenance())
    lines.append("")
    lines.append(TABLE_STYLES)
    lines.append("")
    lines.append("## Table of contents")
    lines.append("")
    for title, _rows in sections:
        lines.append(f"- [{title}](#{slugify(title)})")
    lines.append("")
    for title, rows in sections:
        lines.append(f"## {title}")
        lines.append("")
        lines.append("| " + " | ".join(COLUMNS) + " |")
        lines.append("|" + "|".join(["---"] * len(COLUMNS)) + "|")
        for row in rows:
            cells = row if len(row) == len(COLUMNS) else row + [""] * (
                len(COLUMNS) - len(row)
            )
            cells = cells[:len(COLUMNS)]
            cells = [render_cell(c) for c in cells]
            lines.append("| " + " | ".join(cells) + " |")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _front_matter() -> str:
    return (
        "+++\n"
        "title = \"Cheryl L. Bruno: Contemporary Sources for Joseph Smith Polygamy\"\n"
        'path = "/bruno-contemporary-sources-for-js-polygamy/"\n'
        'extra = {doctype = "resource", maintopic = "polygamy"}\n'
        f'updated = "{datetime.date.today().isoformat()}"\n'
        "+++"
    )


def _provenance() -> str:
    docx_link = f"[{DOCX_FILENAME}](<{DOCX_LINK_URL}>)"
    script_link = f"[parser script]({SCRIPT_URL})"
    return INTRODUCTION.format(docx_link=docx_link, script_link=script_link)


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    repo_root = Path(__file__).resolve().parent.parent
    docx = repo_root / \
        "static/media/Contemporary_Sources_for_JS_Polygamy_(chart)_8.22.26.docx"
    out = repo_root / "content/documents/polygamy/bruno_contemporary_sources.md"
    if argv:
        docx = Path(argv[0])
    if len(argv) > 1:
        out = Path(argv[1])

    if not docx.exists():
        sys.exit(f"docx not found: {docx}")

    sections = parse_table(docx)
    markdown = render_markdown(sections)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(markdown, encoding="utf-8")
    print(f"Wrote {out} ({len(sections)} sections)")
    for title, rows in sections:
        print(f"  - {title!r}: {len(rows)} data rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
