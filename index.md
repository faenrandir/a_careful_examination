---
layout: home
---

A collection of resources, research, and thoughts on the truth-claims, teachings, and culture of The Church of Jesus Christ of Latter-day Saints.

## For your consideration

{% for page in site.pages %}
 {% if page.doctype == 'introductory-resource' %}
<a href="{{ site.baseurl }}{{ page.url }}">{{ page.title }}</a>
 {% endif %}
{% endfor %}

## Resources

<ul>
  {% for page in site.pages %}
     {% if page.doctype == 'resource' %}
      <li><a href="{{ site.baseurl }}{{ page.url }}">{{ page.title }}</a></li>
     {% endif %}
  {% endfor %}
</ul>

## Communication and Response

<ul>
  {% for page in site.pages %}
     {% if page.doctype == 'response' %}
      <li><a href="{{ site.baseurl }}{{ page.url }}">{{ page.title }}</a></li>
     {% endif %}
  {% endfor %}
</ul>

## Snippets

<ul>
  {% for page in site.pages %}
     {% if page.doctype  == 'snippet' %}
      <li><a href="{{ site.baseurl }}{{ page.url }}">{{ page.title }}</a></li>
     {% endif %}
  {% endfor %}
</ul>


