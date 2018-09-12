---
layout: home
---

A collection of resources, research, and thoughts on the truth-claims, teachings, and culture of The Church of Jesus Christ of Latter-day Saints.

## For your initial consideration

{% for page in site.pages %}
 {% if page.doctype == 'resource' and page.introductory %}
<a href="{{ site.baseurl }}{{ page.url }}">{{ page.title }}</a>
 {% endif %}
{% endfor %}

## General Resources

<ul>
  {% for page in site.pages %}
    {% if page.doctype == 'resource' %}
      {% if page.maintopic != 'polygamy' and page.maintopic != 'faith-transitions' %}
      <li><a href="{{ site.baseurl }}{{ page.url }}">{{ page.title }}</a></li>
      {% endif %}
    {% endif %}
  {% endfor %}
</ul>

## Faith Transitions

<ul>
  {% for page in site.pages %}
     {% if page.maintopic == 'faith-transitions' %}
      <li><a href="{{ site.baseurl }}{{ page.url }}">{{ page.title }}</a></li>
     {% endif %}
  {% endfor %}
</ul>

## Polygamy

<ul>
  {% for page in site.pages %}
     {% if page.maintopic == 'polygamy' and page.doctype != 'historical-resource' and page.doctype != 'historical-source' %}
      <li><a href="{{ site.baseurl }}{{ page.url }}">{{ page.title }}</a></li>
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

## Miscellaneous

{% assign sortedpages = site.pages | sort:"doctype" %}

<ul>
  {% for page in sortedpages %}
    {% if page.doctype and page.doctype != 'resource' %}
      {% if page.maintopic != 'polygamy' and page.maintopic != 'faith-transitions' %}
      <li><a href="{{ site.baseurl }}{{ page.url }}">{{ page.title }}</a><span class="doctype-annotation"> {{ page.doctype }}</span></li>
      {% endif %}
    {% endif %}
  {% endfor %}
</ul>
