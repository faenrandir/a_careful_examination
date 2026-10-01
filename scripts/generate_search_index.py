#!/usr/bin/env python3
"""
Generate a simple search index for Zola sites when native search is not working.
Run after `zola build` to create search_index.json
"""

import json
import os
import re
from pathlib import Path
from bs4 import BeautifulSoup

CONTENT_DIR = Path("/home/jtprince/projects/a_careful_examination/content")
OUTPUT_DIR = Path("/home/jtprince/projects/a_careful_examination/docs")
INDEX_FILE = OUTPUT_DIR / "search_index.json"

def extract_text_from_html(html_path):
    """Extract readable text from HTML file."""
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        soup = BeautifulSoup(content, 'html.parser')
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
            script.decompose()
        text = soup.get_text()
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text[:2000]  # Limit snippet length
    except Exception:
        return ""

def get_page_info(html_path):
    """Extract title, URL, and snippet from HTML file."""
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        soup = BeautifulSoup(content, 'html.parser')
        
        # Get title
        title_tag = soup.find('h1') or soup.find('title')
        title = title_tag.get_text().strip() if title_tag else "Untitled"
        
        # Get URL from canonical link or path
        canonical = soup.find('link', rel='canonical')
        if canonical and canonical.get('href'):
            url = canonical['href']
        else:
            # Derive from file path
            rel_path = html_path.relative_to(OUTPUT_DIR)
            if rel_path.name == 'index.html':
                url = '/' + str(rel_path.parent).replace('\\', '/') + '/'
            else:
                url = '/' + str(rel_path).replace('\\', '/')
        
        # Get snippet from first paragraph of content
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='post-content')
        if main_content:
            first_p = main_content.find('p')
            snippet = first_p.get_text().strip()[:300] if first_p else ""
        else:
            # Fallback to body text
            body = soup.find('body')
            if body:
                snippet = body.get_text().strip()[:300]
            else:
                snippet = ""
        
        return {
            "title": title,
            "url": url,
            "snippet": snippet
        }
    except Exception as e:
        print(f"Error processing {html_path}: {e}")
        return None

def main():
    print("Generating search index...")
    
    pages = []
    
    # Walk all HTML files in output directory
    for html_path in OUTPUT_DIR.rglob("*.html"):
        # Skip search page, 404, and taxonomy list pages
        if any(skip in str(html_path) for skip in ['/search/', '/404.html', '/maintopic/index.html', '/doctype/index.html']):
            continue
        
        info = get_page_info(html_path)
        if info and info['snippet']:
            pages.append(info)
    
    print(f"Indexed {len(pages)} pages")
    
    # Write index
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump({"pages": pages}, f, ensure_ascii=False, indent=2)
    
    print(f"Search index written to {INDEX_FILE}")

if __name__ == '__main__':
    main()