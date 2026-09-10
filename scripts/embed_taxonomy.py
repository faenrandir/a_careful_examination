#!/usr/bin/env python3
"""Embed taxonomy data directly into the browse.html template."""
import json
import re
from pathlib import Path

# Read the taxonomy index
with open("docs/taxonomy_index.json") as f:
    data = json.load(f)

# Read the browse template
with open("templates/browse.html", "r") as f:
    content = f.read()

# Generate the JavaScript data
categories_js = json.dumps(data.get("categories", []))
tags_js = json.dumps(data.get("tags", []))

new_script = """<script>
  // Embedded taxonomy data
  const categoriesData = """ + json.dumps(data.get("categories", [])) + """;
  const tagsData = """ + json.dumps(data.get("tags", [])) + """;
  
  function renderTaxonomy(data, listId) {
    const list = document.getElementById(listId);
    if (!list || !data) return;
    
    list.innerHTML = data.map(term => 
      '<li><a href="/a_careful_examination/categories/' + (term.slug || term.name.toLowerCase().replace(/[^a-z0-9]+/g, "-")) + '/">' + term.name + ' (' + (term.count || 0) + ')</a></li>'
    ).join('');
  }
  
  // Render on load
  document.addEventListener('DOMContentLoaded', () => {
    renderTaxonomy(categoriesData, 'categories-list');
    renderTaxonomy(tagsData, 'tags-list');
  });
</script>"""

# Replace the script section
script_pattern = r"<script>.*?</script>"
new_content = re.sub(r"<script>.*?</script>", new_script, content, flags=re.DOTALL)

with open("templates/browse.html", "w") as f:
    f.write(new_content)

print("Updated browse.html with embedded taxonomy data")