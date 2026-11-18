#!/usr/bin/env python3
"""Preview the site locally with live reload (§I.2).

Builds with scripts/build.py, then serves the result at
http://127.0.0.1:1111/a_careful_examination/ and rebuilds when content,
templates, styles, static files, scripts, or config.toml change.

The site's base_url is /a_careful_examination, so a small WSGI app maps that
URL prefix onto docs/. Nothing is written inside docs/, and the mapping
survives each rebuild's removal of docs/.

Usage: python3 scripts/serve.py   (needs `pip install livereload`)
"""

import mimetypes
import sys
from pathlib import Path
from urllib.parse import unquote

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import DOCS, REPO_ROOT, build  # noqa: E402

PORT = 1111
PREFIX = "/a_careful_examination"
WATCHED = ("content", "templates", "sass", "static", "scripts", "config.toml")


def site_app(environ, start_response):
    """Serve files from docs/ under PREFIX; redirect / to PREFIX/."""
    path = unquote(environ.get("PATH_INFO", "/"))
    if path in ("", "/"):
        start_response("302 Found", [("Location", PREFIX + "/")])
        return [b""]
    if not path.startswith(PREFIX + "/"):
        return _not_found(start_response)

    docs = DOCS.resolve()
    target = (docs / path[len(PREFIX) + 1:]).resolve()
    if target.is_dir():
        if not path.endswith("/"):
            start_response("301 Moved Permanently", [("Location", path + "/")])
            return [b""]
        target = target / "index.html"
    if docs not in target.parents or not target.is_file():
        return _not_found(start_response)

    content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
    if content_type.startswith("text/") or content_type.endswith(("javascript", "json")):
        content_type += "; charset=utf-8"
    body = target.read_bytes()
    start_response("200 OK", [("Content-Type", content_type),
                              ("Content-Length", str(len(body)))])
    return [body]


def _not_found(start_response):
    page = DOCS / "404.html"
    body = page.read_bytes() if page.is_file() else b"Not found"
    start_response("404 Not Found", [("Content-Type", "text/html; charset=utf-8"),
                                     ("Content-Length", str(len(body)))])
    return [body]


def main() -> None:
    try:
        from livereload import Server
    except ImportError:
        print(
            "serve.py needs the livereload package. Install it with\n"
            "    pip install livereload\n"
            "or  uv pip install livereload",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        build()
    except RuntimeError as error:
        print(f"Build failed: {error}", file=sys.stderr)
        sys.exit(1)

    def rebuild() -> None:
        try:
            build()
        except RuntimeError as error:
            print(f"Rebuild failed: {error}", file=sys.stderr)

    server = Server(app=site_app)
    for path in WATCHED:
        server.watch(str(REPO_ROOT / path), rebuild)

    print(f"Serving at http://127.0.0.1:{PORT}{PREFIX}/", flush=True)
    print("Press Ctrl+C to stop\n", flush=True)
    try:
        server.serve(port=PORT, host="127.0.0.1")
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
