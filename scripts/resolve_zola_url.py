#!/usr/bin/env python3
"""
Resolve a Zola Markdown file to its rendered URL and open it in a browser.
Automatically starts 'zola serve' if it is not running.
"""

import os
import re
import sys
import subprocess
import time
import webbrowser
import http.client
from urllib.parse import urljoin

DEFAULT_PORT = 1111
DEFAULT_HOST = "localhost"
DEFAULT_URL = f"http://{DEFAULT_HOST}:{DEFAULT_PORT}"


def is_server_running(host, port):
    """Check if the Zola server is responding on the given port."""
    try:
        conn = http.client.HTTPConnection(host, port, timeout=1)
        conn.request("HEAD", "/")
        response = conn.getresponse()
        conn.close()
        return True
    except Exception:
        return False


def start_zola_serve():
    """Start 'zola serve' in the background."""
    print(f"Starting 'zola serve' on port {DEFAULT_PORT}...")
    # Start zola serve. We don't use --open here because we want to 
    # control the specific URL being opened.
    subprocess.Popen(
        ["zola", "serve", "--port", str(DEFAULT_PORT)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True
    )
    # Give it a moment to start
    for _ in range(10):
        time.sleep(0.5)
        if is_server_running(DEFAULT_HOST, DEFAULT_PORT):
            return True
    return False


def get_base_url():
    """Extract base_url from config.toml."""
    try:
        with open("config.toml", "r") as f:
            content = f.read()
            match = re.search(r'^base_url\s*=\s*"([^"]+)"', content, re.MULTILINE)
            if match:
                return match.group(1)
    except FileNotFoundError:
        pass
    return "/"


def resolve_url_path(filepath):
    """
    Resolve the URL path for a given Markdown file.
    Handles 'path', 'slug', and default Zola structure.
    """
    if not os.path.exists(filepath):
        return None

    rel_path = os.path.relpath(filepath, "content")
    
    with open(filepath, "r") as f:
        content = f.read()

    # Match TOML front matter
    fm_match = re.match(r'^\+\+\+\n(.*?)\n\+\+\+', content, re.DOTALL)
    path_override = None
    slug_override = None

    if fm_match:
        fm_content = fm_match.group(1)
        path_match = re.search(r'^path\s*=\s*"([^"]+)"', fm_content, re.MULTILINE)
        if path_match:
            path_override = path_match.group(1)
        
        slug_match = re.search(r'^slug\s*=\s*"([^"]+)"', fm_content, re.MULTILINE)
        if slug_match:
            slug_override = slug_match.group(1)

    # 1. Explicit path override
    if path_override:
        return path_override

    # 2. Section index (_index.md)
    if os.path.basename(filepath) == "_index.md":
        # content/about/_index.md -> /about/
        dir_name = os.path.dirname(rel_path)
        if dir_name == "." or dir_name == "":
            return "/"
        return f"/{dir_name}/"

    # 3. Page index (index.md)
    if os.path.basename(filepath) == "index.md":
        dir_name = os.path.dirname(rel_path)
        return f"/{dir_name}/"

    # 4. Normal page
    dir_name = os.path.dirname(rel_path)
    base_name = os.path.splitext(os.path.basename(filepath))[0]
    
    slug = slug_override or base_name
    
    if dir_name == "." or dir_name == "":
        return f"/{slug}/"
    else:
        return f"/{dir_name}/{slug}/"


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <markdown_file> [--open]")
        sys.exit(1)

    filepath = sys.argv[1]
    should_open = "--open" in sys.argv

    # Ensure we are in the project root
    if not os.path.exists("config.toml") or not os.path.exists("content"):
        print("Error: Must be run from the Zola project root.")
        sys.exit(1)

    # Check if server is running, start if not
    if not is_server_running(DEFAULT_HOST, DEFAULT_PORT):
        if not start_zola_serve():
            print("Error: Could not start 'zola serve'.")
            sys.exit(1)

    path = resolve_url_path(filepath)
    if path is None:
        print(f"Error: Could not resolve path for {filepath}")
        sys.exit(1)

    # Zola serve strips the base_url from the local server paths usually,
    # but we should be careful. Actually, zola serve uses the base_url
    # if it's set in config.toml but it often serves from root.
    # In this project, base_url = "/a_careful_examination"
    
    # Check if we need to include base_url
    # For 'zola serve', it typically serves the site as if it were at the root
    # UNLESS you are using it specifically. 
    # However, let's just use the path relative to the server root.
    
    full_url = urljoin(DEFAULT_URL, path)
    
    print(f"Resolved URL: {full_url}")
    
    if should_open:
        webbrowser.open(full_url)


if __name__ == "__main__":
    main()
