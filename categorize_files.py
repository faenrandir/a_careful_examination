#!/usr/bin/env python3
"""
Categorize all markdown files in the content directory to match config.toml taxonomy.
"""

import os
import re
import tomllib
import tomli_w
from pathlib import Path

CONTENT_ROOT = Path("/home/jtprince/projects/a_careful_examination/content")

# Target categories from config.toml
TARGET_CATEGORIES = [
    "book-of-mormon",
    "joseph-smith",
    "lds-history-leadership",
    "doctrine-teachings",
    "faith-transitions",
    "apologetics-responses",
    "research-primary-sources",
    "social-moral-issues",
    "personal-reflections",
    "other",
]

# Directory to category mapping
DIR_MAPPING = {
    # book-of-mormon
    "documents/book_of_mormon": ["book-of-mormon", "apologetics-responses", "doctrine-teachings"],
    
    # joseph-smith
    "documents/first-vision": ["joseph-smith", "doctrine-teachings"],
    "documents/treasure_digging": ["joseph-smith", "doctrine-teachings"],
    "documents/kinderhook_plates": ["joseph-smith", "apologetics-responses"],
    "documents/polygamy": ["joseph-smith", "lds-history-leadership", "social-moral-issues"],
    
    # lds-history-leadership
    "documents/blacks_and_priesthood-temple_ban": ["lds-history-leadership", "social-moral-issues", "doctrine-teachings"],
    "documents/second_coming": ["lds-history-leadership", "doctrine-teachings"],
    "documents/tithing": ["lds-history-leadership", "doctrine-teachings"],
    "documents/temple": ["lds-history-leadership", "doctrine-teachings"],
    "documents/threefold-nature-of-the-church": ["lds-history-leadership", "doctrine-teachings", "faith-transitions"],
    
    # doctrine-teachings (default for many)
    "documents/faith": ["doctrine-teachings", "faith-transitions"],
    "documents/gospel-fundamentals-2002-god-as-man-and-new-worlds.md": ["doctrine-teachings"],
    "documents/the_six_sources_of_revelation.md": ["doctrine-teachings", "faith-transitions"],
    "documents/morality_transcends_religious_belief": ["doctrine-teachings", "faith-transitions"],
    "documents/family-proclamation": ["doctrine-teachings", "social-moral-issues"],
    "documents/word_of_wisdom": ["doctrine-teachings", "lds-history-leadership"],
    "documents/sexuality": ["doctrine-teachings", "social-moral-issues", "faith-transitions"],
    "documents/womens_issues": ["doctrine-teachings", "social-moral-issues"],
    "documents/same_sex_marriage": ["doctrine-teachings", "social-moral-issues"],
    
    # faith-transitions
    "documents/faith_crisis_study": ["faith-transitions", "personal-reflections", "doctrine-teachings"],
    "documents/motivation_to_resign": ["faith-transitions", "personal-reflections"],
    "documents/mixed_faith_families": ["faith-transitions", "personal-reflections", "social-moral-issues"],
    "documents/about_apostates": ["faith-transitions", "lds-history-leadership", "personal-reflections"],
    "documents/what_I_have_shared_with_my_children": ["faith-transitions", "personal-reflections"],
    "documents/why_it_matters": ["faith-transitions", "personal-reflections"],
    "documents/the_50_50_scenario.md": ["faith-transitions", "personal-reflections", "doctrine-teachings"],
    "documents/seen_jesus": ["faith-transitions", "doctrine-teachings"],
    
    # apologetics-responses
    "documents/falsehoods_contradictions_and_silliness": ["apologetics-responses", "doctrine-teachings", "lds-history-leadership"],
    "documents/light-and-truth-letter": ["apologetics-responses", "book-of-mormon"],
    "documents/helps_and_harms": ["apologetics-responses", "social-moral-issues", "faith-transitions"],
    "documents/hermetically_sealed_stacked_deck": ["apologetics-responses", "doctrine-teachings", "faith-transitions"],
    "documents/the_dominant_narrative_cannot_be_sustained": ["apologetics-responses", "lds-history-leadership"],
    "documents/book_of_abraham": ["apologetics-responses", "book-of-mormon", "joseph-smith"],
    "documents/book_of_enoch": ["apologetics-responses", "book-of-mormon", "research-primary-sources"],
    "documents/jst": ["apologetics-responses", "doctrine-teachings"],
    "documents/visionary_and_prophetic_experience": ["apologetics-responses", "doctrine-teachings", "faith-transitions"],
    "documents/spiritual_experiences-testimony-holy_ghost": ["apologetics-responses", "doctrine-teachings", "faith-transitions"],
    
    # research-primary-sources
    "documents/leaked": ["research-primary-sources", "lds-history-leadership", "other"],
    
    # social-moral-issues
    "documents/lgbt": ["social-moral-issues", "doctrine-teachings", "faith-transitions"],
    
    # personal-reflections
    "documents/my_beliefs": ["personal-reflections", "faith-transitions"],
    "documents/my_journey": ["personal-reflections", "faith-transitions"],
    
    # other / misc
    "documents/questions": ["other", "doctrine-teachings"],
    "documents/miscellaneous": ["other", "doctrine-teachings"],
    "documents/christianity": ["doctrine-teachings", "other"],
    "documents/science": ["doctrine-teachings", "apologetics-responses"],
    "documents/truth_claim_summaries": ["apologetics-responses", "doctrine-teachings", "book-of-mormon"],
    "documents/early_testimonies_unreliable.md": ["apologetics-responses", "joseph-smith", "book-of-mormon"],
    "documents/endorsements.md": ["other", "personal-reflections"],
    "documents/clarke_commentary_originally_published_1810_1826.md": ["joseph-smith", "research-primary-sources"],
    "documents/conclusion_surrogate_parent_hypothesis.md": ["joseph-smith", "doctrine-teachings"],
    "documents/books_donated_by_joseph_smith_to_nauvoo_library.md": ["joseph-smith", "research-primary-sources"],
    "documents/kinderhook_plates": ["joseph-smith", "apologetics-responses"],
    "documents/books_donated_by_joseph_smith_to_nauvoo_library.md": ["joseph-smith", "research-primary-sources"],
    "documents/any_opposed": ["doctrine-teachings", "lds-history-leadership"],
    
    # communications - mostly apologetics-responses
    "communications": ["apologetics-responses", "other"],
    
    # psychology_of_religion, secular_humanism
    "psychology_of_religion": ["doctrine-teachings", "faith-transitions", "other"],
    "secular_humanism": ["doctrine-teachings", "other"],
    
    # root level files
    "search.md": ["other"],
    "vetting-editorial.md": ["other"],
    "additional_resources.md": ["other"],
}

# Special case file overrides
FILE_OVERRIDES = {
    "documents/faith/faith_and_the_light_switch.md": ["doctrine-teachings", "faith-transitions"],
    "documents/book_of_mormon/links_to_parallels_to_1800s_theology.md": ["book-of-mormon", "apologetics-responses"],
    "documents/my_beliefs/wholehearted_parenting_manifesto.md": ["personal-reflections", "faith-transitions"],
    "documents/communications/response_to_faith_of_a_science_teacher.md": ["apologetics-responses", "truth-claims"],  # truth-claims not in config, use doctrine-teachings
}

# Files to skip (index files, etc.)
SKIP_PATTERNS = [
    "_index.md",
    "/about/",
    "/browse/",
    "/recommended/",
]

def get_mapping_for_file(filepath):
    """Get the category mapping for a given file path."""
    rel_path = filepath.relative_to(CONTENT_ROOT)
    rel_str = str(rel_path)
    
    # Check file overrides first
    for pattern, cats in FILE_OVERRIDES.items():
        if rel_str.endswith(pattern) or pattern in rel_str:
            return cats
    
    # Check directory mappings (longest match first)
    for pattern, cats in sorted(DIR_MAPPING.items(), key=lambda x: -len(x[0])):
        if rel_str.startswith(pattern):
            return cats
    
    return ["other"]

def parse_frontmatter(content):
    """Parse TOML frontmatter from markdown content."""
    match = re.match(r'^\+\+\+\n(.*?)\n\+\+\+', content, re.DOTALL)
    if not match:
        return None, content
    
    frontmatter_str = match.group(1)
    try:
        fm = tomllib.loads(frontmatter_str)
        # Ensure fm is a dict
        if not isinstance(fm, dict):
            return None, content
        return fm, content[match.end():]
    except tomllib.TOMLDecodeError as e:
        print(f"Error parsing frontmatter: {e}")
        return None, content

def serialize_frontmatter(fm):
    """Serialize frontmatter to TOML format."""
    import tomli_w
    return "+++\n" + tomli_w.dumps(fm) + "+++\n"

def process_file(filepath):
    """Process a single markdown file."""
    # Skip index files and special pages
    for pattern in SKIP_PATTERNS:
        if pattern in str(filepath):
            return False
    
    content = filepath.read_text(encoding='utf-8')
    fm, body = parse_frontmatter(content)
    
    if fm is None:
        return False
    
    # Get mapped categories
    mapped_cats = get_mapping_for_file(filepath)
    
    # Get existing categories
    existing_cats = []
    if "taxonomies" in fm and isinstance(fm["taxonomies"], dict) and "categories" in fm["taxonomies"]:
        existing_cats = fm["taxonomies"]["categories"]
        if isinstance(existing_cats, str):
            existing_cats = [existing_cats]
    
    # Fix malformed categories
    cat_fixes = {
        "Beliefs": "doctrine-teachings",
        "Book of Mormon": "book-of-mormon",
        "Truth-Claims": "doctrine-teachings",
        "My beliefs": "personal-reflections",
        "truth-claims": "doctrine-teachings",
        "sociology-and-psychology": "faith-transitions",
    }
    
    fixed_cats = []
    for cat in existing_cats:
        if cat in cat_fixes:
            fixed_cats.append(cat_fixes[cat])
        elif cat in TARGET_CATEGORIES:
            fixed_cats.append(cat)
    
    # Combine: existing (fixed) + mapped, deduplicate
    all_cats = list(dict.fromkeys(fixed_cats + mapped_cats))
    
    # Update frontmatter
    if "taxonomies" not in fm:
        fm["taxonomies"] = {}
    fm["taxonomies"]["categories"] = all_cats
    
    # Write back
    new_content = serialize_frontmatter(fm) + body
    filepath.write_text(new_content, encoding='utf-8')
    
    return True

def main():
    processed = 0
    skipped = 0
    
    for md_file in CONTENT_ROOT.rglob("*.md"):
        if process_file(md_file):
            processed += 1
        else:
            skipped += 1
    
    print(f"Processed: {processed}, Skipped: {skipped}")

if __name__ == "__main__":
    main()