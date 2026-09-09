#!/usr/bin/env python3
"""
Generate taxonomy index JSON for sidebar and tag clouds.
Run after `zola build` to create taxonomy_index.json
"""

import json
import os
from pathlib import Path

CONTENT_DIR = Path("/home/jtprince/projects/a_careful_examination/content")
OUTPUT_DIR = Path("/home/jtprince/projects/a_careful_examination/docs")
INDEX_FILE = OUTPUT_DIR / "taxonomy_index.json"

def main():
    print("Generating taxonomy index...")
    
    maintopic_terms = {}
    doctype_terms = {}
    
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
            
            # Simple TOML parsing for taxonomies
            maintopic = None
            doctype = None
            
            for line in fm_text.split('\n'):
                line = line.strip()
                if line.startswith('taxonomies.maintopic'):
                    # Extract array value
                    val = line.split('=', 1)[1].strip()
                    if val.startswith('[') and val.endswith(']'):
                        items = val[1:-1].split(',')
                        for item in items:
                            item = item.strip().strip('"\'')
                            if item:
                                maintopic_terms[item] = maintopic_terms.get(item, 0) + 1
                elif line.startswith('taxonomies.doctype'):
                    val = line.split('=', 1)[1].strip()
                    if val.startswith('[') and val.endswith(']'):
                        items = val[1:-1].split(',')
                        for item in items:
                            item = item.strip().strip('"\'')
                            if item:
                                doctype_terms[item] = doctype_terms.get(item, 0) + 1
        except Exception as e:
            print(f"Error processing {md_path}: {e}")
    
    # Convert to sorted list of objects
    maintopic_list = sorted(
        [{"name": k, "count": v, "slug": k.lower().replace(' ', '-').replace('_', '-')} 
         for k, v in maintopic_terms.items()],
        key=lambda x: x['name']
    )
    
    doctype_list = sorted(
        [{"name": k, "count": v, "slug": k.lower().replace(' ', '-').replace('_', '-')} 
         for k, v in doctype_terms.items()],
        key=lambda x: x['name']
    )
    
    data = {
        "maintopic": maintopic_list,
        "doctype": doctype_list
    }
    
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Taxonomy index written to {INDEX_FILE}")
    print(f"  {len(maintopic_list)} maintopic terms")
    print(f"  {len(doctype_list)} doctype terms")

if __name__ == '__main__':
    main()