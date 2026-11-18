"""Styles, homepage ordering, article metadata, and contrast (spec/invariants/presentation.md)."""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SASS = REPO_ROOT / "sass"
TOKENS = SASS / "_tokens.scss"


def test_colors_only_in_tokens():
    """§V.8: no hex colors outside _tokens.scss and no CSS custom properties."""
    offenders = []
    for path in sorted(SASS.glob("*.scss")):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if path != TOKENS and re.search(r"#[0-9a-fA-F]{3,8}\b", line):
                offenders.append(f"{path.name}:{number}: {line.strip()}")
            if "var(--" in line:
                offenders.append(f"{path.name}:{number}: {line.strip()}")
    assert not offenders, "colors outside the token file:\n" + "\n".join(offenders)


def _top_level_rules(css: str) -> list[tuple[list[str], str]]:
    """(selectors, declarations) for rules outside any @-block, in source order."""
    rules, depth, start, selector = [], 0, 0, ""
    for i, char in enumerate(css):
        if char == "{":
            if depth == 0:
                selector, start = css[start:i].strip(), i + 1
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                if not selector.startswith("@"):
                    rules.append(([s.strip() for s in selector.split(",")], css[start:i]))
                start = i + 1
    return rules


def _margin_left(css: str, selector: str) -> float:
    """The last top-level left margin, in px, that the compiled CSS gives one selector."""
    value = None
    for selectors, body in _top_level_rules(css):
        if selector not in selectors:
            continue
        for prop, val in re.findall(r"(margin(?:-left)?)\s*:\s*([^;]+)", body):
            parts = val.split()
            if prop == "margin-left":
                value = parts[0]
            else:
                value = parts[{1: 0, 2: 1, 3: 1, 4: 3}[len(parts)]]
    assert value is not None and value.endswith("px"), f"no px left margin for {selector}: {value}"
    return float(value[:-2])


def test_lists_indent_past_paragraphs(site):
    """§V.9: article lists start 40px inside paragraph text."""
    css = (site / "main.css").read_text(encoding="utf-8")
    paragraph = _margin_left(css, ".post-content p")
    for selector in (".post-content ul", ".post-content ol"):
        assert _margin_left(css, selector) - paragraph == 40, f"{selector} is not 40px past .post-content p"


def test_homepage_recent_is_newest_first(site):
    """§V.10: homepage "Recently Updated" dates are in descending order (§B.4)."""
    html = (site / "index.html").read_text(encoding="utf-8")
    section = html.split('class="recently-updated"', 1)[1].split("</section>", 1)[0]
    dates = re.findall(r'<time datetime="(\d{4}-\d{2}-\d{2})"', section)
    assert len(dates) >= 2, "the homepage recent list is empty"
    assert dates == sorted(dates, reverse=True), f"not newest first: {dates}"
    assert len(set(dates)) > 1, "every listed page shares one date; ordering cannot be checked"


def test_article_shows_one_updated_date(site):
    """§V.11: an article page shows its updated date once."""
    checked = 0
    for page in site.glob("*/index.html"):
        html = page.read_text(encoding="utf-8")
        if 'class="article-meta"' not in html:
            continue
        checked += 1
        assert 'class="last-update"' not in html, f"{page.parent.name} repeats the date"
        assert html.count('class="resource-updated"') <= 1, f"{page.parent.name} shows two dates"
    assert checked > 100, f"only {checked} article pages found"


def _token(name: str) -> str:
    match = re.search(rf"^\${name}:\s*(#[0-9a-fA-F]{{6}})", TOKENS.read_text(encoding="utf-8"), re.M)
    assert match, f"${name} is not a 6-digit hex token"
    return match.group(1)


def _luminance(hex_color: str) -> float:
    channels = [int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def test_text_colors_meet_contrast_minimum():
    """§V.12: $ink-muted and $accent reach 4.5:1 on $paper."""
    paper = _luminance(_token("paper"))
    for name in ("ink-muted", "accent"):
        color = _luminance(_token(name))
        ratio = (max(paper, color) + 0.05) / (min(paper, color) + 0.05)
        assert ratio >= 4.5, f"${name} on $paper is {ratio:.2f}:1"
