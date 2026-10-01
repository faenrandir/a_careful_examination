#!/usr/bin/env python3
"""
Migration script to convert old taxonomies (maintopic, doctype) to new structure:
- categories (single primary)
- tags (multiple cross-cutting)
- extra.type (resource type)
"""

import os
import re
import copy
import tomllib
import tomli_w
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

CONTENT_DIR = Path("/home/jtprince/projects/a_careful_examination/content")

def parse_frontmatter(content: str) -> Tuple[Dict, str]:
    """Parse TOML frontmatter from markdown content"""
    if not content.startswith('+++'):
        return {}, content
    
    parts = content.split('+++', 2)
    if len(parts) < 3:
        return {}, content
    
    try:
        fm = tomllib.loads(parts[1])
        if not isinstance(fm, dict):
            fm = {}
        body = parts[2]
        return fm, body
    except Exception as e:
        print(f"Warning: Failed to parse frontmatter: {e}")
        return {}, content

# Tag suggestions based on content analysis
# These are additional tags to add based on content/title analysis
CONTENT_TAG_RULES = [
    (r"seer\s*stone", ["seer-stones"]),
    (r"\btranslation\b", ["translation"]),
    (r"\bpolygamy\b|\bplural\s*marriage\b", ["polygamy"]),
    (r"first\s*vision", ["first-vision"]),
    (r"book\s*of\s*mormon.*historicity|historicity.*book\s*of\s*mormon", ["book-of-mormon-historicity"]),
    (r"\bprophecy\b|\bprophetic\b", ["prophecy"]),
    (r"\btestimony\b", ["testimony"]),
    (r"\bepistemolog", ["epistemology"]),
    (r"\brace\b|\bpriesthood\s*ban\b", ["race", "priesthood-ban"]),
    (r"\bgender\b|\bwomen\b|\bpatriarchy\b", ["gender"]),
    (r"\bsexuality\b|\bLGBTQ\b|\bhomosexual\b", ["sexuality", "lgbt"]),
    (r"word\s*of\s*wisdom", ["word-of-wisdom"]),
    (r"faith\s*(crisis|transition)", ["faith-transition"]),
    (r"\bapologetic", ["apologetics"]),
    (r"\bprimary\s*source\b|\bhistorical\s*document", ["primary-source"]),
    (r"\bscholar\b|\bacademic\b", ["scholarship"]),
    (r"\bJoseph\s*Smith\b", ["joseph-smith"]),
    (r"\bBook\s*of\s*Mormon\b", ["book-of-mormon"]),
    (r"\btemple\b", ["temple"]),
    (r"\bDNA\b|\bDNA\b", ["dna"]),
    (r"\barchaeolog", ["archaeology"]),
    (r"\bgeograph", ["geography"]),
    (r"\bDNA\b", ["dna"]),
]

# Featured articles (Start Here) - by path
FEATURED_PATHS = {
    "/to-peek-behind-the-curtain/",
    "/five-key-facts/",
    "/truth-claim-summaries-and-apologetics/",
    "/questions-to-ask/",
    "/the-significance-of-the-seer-stone/",
    "/why-should-examine-evidence/",
    "/why-it-matters/",
    "/lds-indoctrination-and-retentive-socialization/",
    "/the-three-fold-nature-lds-church-corporate-totalistic-individual-growth/",
    "/you-can-leave-the-church-but-you-cant-leave-it-alone/",
}

# Primary category mapping from old maintopic
CATEGORY_MAP = {
    "book-of-mormon": "book-of-mormon",
    "book-of-mormon-witnesses": "book-of-mormon",
    "polygamy": "joseph-smith",
    "first-vision": "joseph-smith",
    "magic": "joseph-smith",
    "treasure-digging": "joseph-smith",
    "race-and-priesthood": "lds-history-leadership",
    "transparency": "lds-history-leadership",
    "second-coming": "lds-history-leadership",
    "helps-and-harms": "lds-history-leadership",
    "epistemology": "doctrine-teachings",
    "faith": "doctrine-teachings",
    "temple": "doctrine-teachings",
    "family-proclamation": "doctrine-teachings",
    "lgbt": "doctrine-teachings",
    "sexuality": "doctrine-teachings",
    "word-of-wisdom": "doctrine-teachings",
    "morality_transcends_religious_belief": "doctrine-teachings",
    "science": "doctrine-teachings",
    "faith-transitions": "faith-transitions",
    "faith_crisis_study": "faith-transitions",
    "about_apostates": "faith-transitions",
    "mixed_faith_families": "faith-transitions",
    "spiritual_experiences-testimony-holy_ghost": "faith-transitions",
    "falsehoods_contradictions_and_silliness": "apologetics-responses",
    "apologetics": "apologetics-responses",
    "links": "research-primary-sources",
    "transcript": "research-primary-sources",
    "quotation": "research-primary-sources",
    "compilation": "research-primary-sources",
    "historical-resource": "research-primary-sources",
    "historical-source": "research-primary-sources",
    "race-and-priesthood": "social-moral-issues",
    "lgbt": "social-moral-issues",
    "gender": "social-moral-issues",
    "sexuality": "social-moral-issues",
    "family-proclamation": "social-moral-issues",
    "my_beliefs": "personal-reflections",
    "my_journey": "personal-reflections",
    "motivation_to_resign": "personal-reflections",
    "what_I_have_shared_with_my_children": "personal-reflections",
    # fallback
    "miscellaneous": "other",
    "communications": "other",
    "leaked": "other",
    "secular_humanism": "other",
    "psychology_of_religion": "other",
    "christianity": "other",
    "jst": "other",
    "book_of_abraham": "other",
    "book_of_enoch": "other",
    "visionary_and_prophetic_experience": "other",
    "the_dominant_narrative_cannot_be_sustained": "other",
    "light-and-truth-letter": "other",
    "treasure_digging": "other",
    "the_50_50_scenario": "other",
    "the_six_sources_of_revelation": "other",
    "threefold-nature-of-the-church": "other",
    "hermetically_sealed_stacked_deck": "other",
    "kinderhook_plates": "other",
    "flood": "other",
    "tithing": "other",
    "why_examine": "other",
    "why_it_matters": "other",
    "endorsements": "other",
}

# Featured articles (Start Here) - by path
FEATURED_PATHS = {
    "/to-peek-behind-the-curtain/",
    "/five-key-facts/",
    "/truth-claim-summaries-and-apologetics/",
    "/questions-to-ask/",
    "/the-significance-of-the-seer-stone/",
    "/why-should-examine-evidence/",
    "/why-it-matters/",
    "/lds-indoctrination-and-retentive-socialization/",
    "/the-three-fold-nature-lds-church-corporate-totalistic-individual-growth/",
    "/you-can-leave-the-church-but-you-cant-leave-it-alone/",
}

# Resource type mapping from doctype
DOCTYPE_TO_TYPE = {
    "analysis": "analysis",
    "short-analysis": "short-analysis",
    "short-essay": "essay",
    "essay": "essay",
    "transcript": "transcript",
    "email-transcript": "transcript",
    "email-communication-transcript": "transcript",
    "quotation": "quotation",
    "compilation": "compilation",
    "short-compilation": "compilation",
    "response": "response",
    "short-summary": "short-summary",
    "excerpt": "excerpt",
    "book-excerpt": "book-excerpt",
    "book-exerpt": "book-excerpt",
    "notes": "notes",
    "personal-history": "personal",
    "personal-letter": "personal",
    "personal": "personal",
    "resource": "resource",
    "historical-resource": "historical-resource",
    "historical-source": "historical-source",
    "list-of-resources": "list-of-resources",
    "definitions": "definitions",
    "discussion": "discussion",
    "analogy": "analogy",
    "infographic": "infographic",
    "meme": "meme",
    "shower-thought": "shower-thought",
    "good-ideas": "good-ideas",
    "survey": "survey",
    "report": "report",
    "book-excerpt": "book-excerpt",
    "expert-survey": "survey",
    "footnote": "notes",
    "table": "list-of-resources",
    "links": "list-of-resources",
    "anecdotal": "notes",
}

def extract_tags_from_content(title: str, content: str, existing_tags: List[str]) -> List[str]:
    """Extract additional tags from content analysis"""
    tags = set(existing_tags)
    text = (title + " " + content[:2000]).lower()
    
    for pattern, tag_list in CONTENT_TAG_RULES:
        if re.search(pattern, text, re.IGNORECASE):
            tags.update(tag_list)
    
    return sorted(tags)

def parse_frontmatter(content: str) -> Tuple[Dict, str]:
    """Parse TOML frontmatter from markdown content"""
    if not content.startswith('+++'):
        return {}, content
    
    parts = content.split('+++', 2)
    if len(parts) < 3:
        return {}, content
    
    try:
        fm = tomllib.loads(parts[1])
        if not isinstance(fm, dict):
            fm = {}
        body = parts[2]
        return fm, body
    except Exception as e:
        print(f"Warning: Failed to parse frontmatter: {e}")
        return {}, content

def serialize_frontmatter(fm: Dict) -> str:
    """Serialize frontmatter dict to TOML string using tomli_w"""
    # Remove None values
    clean_fm = {k: v for k, v in fm.items() if v is not None}
    toml_str = tomli_w.dumps(clean_fm)
    return '+++\n' + toml_str + '+++\n'

def migrate_file(filepath: Path, dry_run: bool = True) -> Dict:
    """Migrate a single file's frontmatter"""
    content = filepath.read_text(encoding='utf-8')
    fm, body = parse_frontmatter(content)
    
    if not fm:
        return {"file": str(filepath), "status": "no_frontmatter", "changes": []}
    
    # Check if this is a section index file (_index.md)
    is_section_index = filepath.name == "_index.md"
    
    changes = []
    old_fm = copy.deepcopy(fm)
    
    # Get old taxonomies
    old_maintopic = fm.get('taxonomies', {}).get('maintopic', [])
    old_doctype = fm.get('taxonomies', {}).get('doctype', [])
    
    # For section index files (_index.md), don't add taxonomies
    # Zola section frontmatter doesn't support taxonomies field
    if not is_section_index:
        # Ensure taxonomies dict exists
        if 'taxonomies' not in fm:
            fm['taxonomies'] = {}
        
        # Map maintopic -> categories (single primary)
        new_categories = []
        for mt in old_maintopic:
            if mt in CATEGORY_MAP:
                new_categories.append(CATEGORY_MAP[mt])
            else:
                new_categories.append(mt)  # fallback
        
        # Use first category as primary, or 'other' if none
        primary_category = new_categories[0] if new_categories else "other"
        fm['taxonomies']['categories'] = [primary_category]
        
        # Map doctype + content analysis -> tags
        existing_tags = list(fm.get('taxonomies', {}).get('tags', []))
        new_tags = set(existing_tags)
        
        # Add tags from doctype
        for dt in old_doctype:
            if dt in DOCTYPE_TO_TYPE:
                new_tags.add(DOCTYPE_TO_TYPE[dt])
        
        # Extract tags from content
        title = fm.get('title', '')
        content_text = body
        new_tags.update(extract_tags_from_content(title, content_text, list(new_tags)))
        
        fm['taxonomies']['tags'] = sorted(new_tags)
        
        # Remove old taxonomies
        if 'maintopic' in fm.get('taxonomies', {}):
            del fm['taxonomies']['maintopic']
        if 'doctype' in fm.get('taxonomies', {}):
            del fm['taxonomies']['doctype']
    else:
        # For section index, remove old taxonomies if present
        if 'taxonomies' in fm:
            del fm['taxonomies']
    
    # Add extra.type from doctype (for all files)
    if 'extra' not in fm:
        fm['extra'] = {}
    
    # Determine resource type from first doctype
    resource_type = "notes"  # default
    for dt in old_doctype:
        if dt in DOCTYPE_TO_TYPE:
            resource_type = DOCTYPE_TO_TYPE[dt]
            break
    fm['extra']['type'] = resource_type
    
    # Add featured flag (for pages, not sections)
    if not is_section_index:
        path = fm.get('path', '')
        fm['extra']['featured'] = path in FEATURED_PATHS
    
    # Add importance for sorting (1-10, higher = more important)
    if fm['extra'].get('featured'):
        fm['extra']['importance'] = 10
    elif 'extra' in old_fm and 'importance' in old_fm.get('extra', {}):
        fm['extra']['importance'] = old_fm['extra']['importance']
    else:
        fm['extra']['importance'] = 5
    
    # Track changes
    if old_fm != fm:
        changes.append("taxonomies migrated")
        if 'taxonomies' in fm:
            changes.append(f"categories: {fm['taxonomies'].get('categories')}")
            changes.append(f"tags: {fm['taxonomies'].get('tags')}")
        else:
            changes.append("taxonomies removed (section index)")
        changes.append(f"extra.type: {fm['extra'].get('type')}")
        changes.append(f"extra.featured: {fm['extra'].get('featured')}")
    
    # Write if not dry run
    if not dry_run and changes:
        new_content = serialize_frontmatter(fm) + '\n' + body.lstrip('\n')
        filepath.write_text(new_content, encoding='utf-8')
    
    return {
        "file": str(filepath.relative_to(CONTENT_DIR)),
        "status": "migrated" if changes else "unchanged",
        "changes": changes,
        "old_categories": old_maintopic,
        "new_categories": fm.get('taxonomies', {}).get('categories'),
        "new_tags": fm.get('taxonomies', {}).get('tags'),
        "resource_type": fm['extra'].get('type'),
        "featured": fm['extra'].get('featured'),
    }

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Migrate taxonomies to new structure')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without writing')
    parser.add_argument('--apply', action='store_true', help='Apply changes')
    args = parser.parse_args()
    
    if not args.dry_run and not args.apply:
        print("Use --dry-run to preview or --apply to write changes")
        return
    
    dry_run = args.dry_run
    
    print(f"Scanning {CONTENT_DIR}...")
    md_files = list(CONTENT_DIR.rglob("*.md"))
    print(f"Found {len(md_files)} markdown files")
    
    results = []
    for filepath in md_files:
        result = migrate_file(filepath, dry_run=dry_run)
        results.append(result)
    
    # Summary
    migrated = sum(1 for r in results if r['status'] == 'migrated')
    unchanged = sum(1 for r in results if r['status'] == 'unchanged')
    errors = sum(1 for r in results if r['status'] == 'error')
    
    print(f"\n--- Summary ---")
    print(f"Total files: {len(results)}")
    print(f"Migrated: {migrated}")
    print(f"Unchanged: {unchanged}")
    print(f"Errors: {errors}")
    
    # Show some examples
    print(f"\n--- Sample Migrations ---")
    for r in results:
        if r['status'] == 'migrated':
            print(f"  {r['file']}")
            print(f"    Old maintopic: {r['old_categories']}")
            print(f"    New categories: {r['new_categories']}")
            print(f"    New tags: {r['new_tags']}")
            print(f"    Resource type: {r['resource_type']}")
            print(f"    Featured: {r['featured']}")
            print()
    
    # Featured items
    featured = [r for r in results if r.get('featured')]
    print(f"--- Featured Articles ({len(featured)}) ---")
    for r in featured:
        print(f"  {r['file']}")

if __name__ == '__main__':
    main()