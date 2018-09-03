---
layout: home
---

## Pages

<ul>
  {% for page in site.pages %}
     {% if page.doctype %}
      <li><a href="{{ site.baseurl }}{{ page.url }}">{{ page.title }}</a></li>
     {% endif %}
  {% endfor %}
</ul>

## Other junk

<ul>
  {% for page in site.pages %}
     {% if page.doctype == null %}
      <li>{{ page.title }} ==> {{ page.url }} </li>
     {% endif %}
  {% endfor %}
</ul>
