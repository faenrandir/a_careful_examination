#!/usr/bin/env python3
"""Post-process generated HTML files to fix absolute links."""
import re
from pathlib import Path

BASE_URL = "/a_careful_examination"
DOCS_DIR = Path("docs")

# Pattern to match absolute links that need base_url prefix
# Matches href="/path/" but not href="/a_careful_examination/..." or href="//" or href="http"
LINK_PATTERN = re.compile(r'href="(/[^"/][^"]*)"')

def fix_file(filepath: Path) -> bool:
    content = filepath.read_text(encoding='utf-8')
    
    def replace_link(match):
        href = match.group(1)
        if href.startswith('/a_careful_examination/'):
            return match.group(0)  # Already has base_url
        if href.startswith('//') or href.startswith('http'):
            return match.group(0)  # External or protocol-relative URL
        return f'href="{BASE_URL}{href}"'
    
    new_content = LINK_PATTERN.sub(replace_link, content)
    
    if new_content != content:
        filepath.write_text(new_content, encoding='utf-8')
        return True
    return False

def main():
    fixed = 0
    for html_file in Path("docs").rglob("*.html"):
        if fix_file(html_file):
            print(f"Fixed: {html_file}")
            fixed += 1
    
    print(f"Fixed {fixed} files")

if __name__ == "__main__":
    main()
