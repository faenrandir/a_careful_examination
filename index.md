---
layout: home
---

A collection of resources, research, and thoughts on the truth-claims, teachings, and culture of The Church of Jesus Christ of Latter-day Saints.

## For your initial consideration

{% for page in site.pages %}
 {% if page.doctype == 'introductory-resource' %}
<a href="{{ site.baseurl }}{{ page.url }}">{{ page.title }}</a>
 {% endif %}
{% endfor %}

## Pages

I'm working on organizing these pages.

<ul>
  {% for page in site.pages %}
    {% if page.doctype %}
      {% if page.maintopic != 'polygamy' and page.maintopic != 'faith-transitions' %}
      <li><a href="{{ site.baseurl }}{{ page.url }}">{{ page.title }}</a> <span class="resource-type-listing">{{ page.doctype }}</span></li>
      {% endif %}
    {% endif %}
  {% endfor %}
</ul>

## Faith Transitions

<ul>
  {% for page in site.pages %}
     {% if page.maintopic == 'faith-transitions' %}
      <li><a href="{{ site.baseurl }}{{ page.url }}">{{ page.title }}</a>  <span class="resource-type-listing">{{ page.doctype }}</span></li>
     {% endif %}
  {% endfor %}
</ul>

## Polygamy

<ul>
  {% for page in site.pages %}
     {% if page.maintopic == 'polygamy' and page.doctype != 'historical-resource' and page.doctype != 'historical-source' %}
      <li><a href="{{ site.baseurl }}{{ page.url }}">{{ page.title }}</a>  <span class="resource-type-listing">{{ page.doctype }}</span></li>
     {% endif %}
  {% endfor %}
</ul>

### Polygmay historical resources

<ul>
  {% for page in site.pages %}
     {% if page.maintopic == 'polygamy' and page.doctype == 'historical-resource' or page.doctype == 'historical-source' %}
      <li><a href="{{ site.baseurl }}{{ page.url }}">{{ page.title }}</a></li>
     {% endif %}
  {% endfor %}
</ul>


<!--

## Truth-claims

<ul>
  {% for page in site.pages %}
     {% if page.maintopic == 'truth-claims' %}
      <li><a href="{{ site.baseurl }}{{ page.url }}">{{ page.title }}</a> [{{ page.doctype }}]</li>
     {% endif %}
  {% endfor %}
</ul>


## Uncategorized

<ul>
  {% for page in site.pages %}
     {% unless page.maintopic %}
      <li><a href="{{ site.baseurl }}{{ page.url }}">{{ page.title }}</a> [{{ page.doctype }}]</li>
     {% endunless %}
  {% endfor %}
</ul>


-->
