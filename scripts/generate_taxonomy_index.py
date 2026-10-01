#!/usr/bin/env python3
"""
Generate taxonomy index JSON for sidebar and tag clouds.
Run after `zola build` to create taxonomy_index.json
"""

import json
import re
from pathlib import Path
import tomllib

CONTENT_DIR = Path("/home/jtprince/projects/a_careful_examination/content")
OUTPUT_DIR = Path("/home/jtprince/projects/a_careful_examination/docs")
INDEX_FILE = OUTPUT_DIR / "taxonomy_index.json"

def main():
    print("Generating taxonomy index...")
    
    categories_terms = {}
    tags_terms = {}
    
    # Walk all markdown files in content directory
    for md_path in CONTENT_DIR.rglob("*.md"):
        try:
            with open(md_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse frontmatter
            if not content.startswith('+++'):
                continue
            
            parts = content.split('+++', 2)
            if len(parts) < 3:
                continue
            
            fm_text = parts[1].strip()
            
            # Parse TOML frontmatter
            try:
                fm = tomllib.loads(fm_text)
            except Exception:
                continue
            
            # Extract categories and tags from taxonomies
            taxonomies = fm.get('taxonomies', {})
            categories = taxonomies.get('categories', [])
            tags = taxonomies.get('tags', [])
            
            for cat in categories:
                if isinstance(cat, str):
                    categories_terms[cat] = categories_terms.get(cat, 0) + 1
            
            for tag in tags:
                if isinstance(tag, str):
                    tags_terms[tag] = tags_terms.get(tag, 0) + 1
                    
        except Exception as e:
            print(f"Error processing {md_path}: {e}")
    
    # Convert to sorted list of objects
    categories_list = sorted(
        [{"name": k, "count": v, "slug": k.lower().replace(' ', '-').replace('_', '-')} 
         for k, v in categories_terms.items()],
        key=lambda x: x['name']
    )
    
    tags_list = sorted(
        [{"name": k, "count": v, "slug": k.lower().replace(' ', '-').replace('_', '-')} 
         for k, v in tags_terms.items()],
        key=lambda x: x['name']
    )
    
    data = {
        "categories": categories_list,
        "tags": tags_list
    }
    
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Taxonomy index written to {INDEX_FILE}")
    print(f"  {len(categories_list)} categories")
    print(f"  {len(tags_list)} tags")

if __name__ == '__main__':
    main()