{% for name, description, skills in zip(main.name, main.description, main.main_skills) %}
# {{ name[0] }} 
{{ description[0] }}
###### Main skills: {{skills[0]}}
{% endfor %}

## Featured
{% for post in featured.title %}
{{ post | join('\n') }}

{% endfor %}

## Experience
{% for basic, description in zip(experience.basic, experience.description) %}
### {{basic[0]}} — {{basic[1]}}
> *{{basic[2]}}*

{{ description | join('\n\n') }}

{% endfor %}

## Education
{% for basic, description in zip(education.basic, education.description) %}
### {{basic[1]}}
> {{basic[0]}} — {{basic[2]}}

{% if len(description) > 1%}
{{description[0]}}
{% if len(description) > 2 %}
{{description[1]}}
{% endif %}
{% endif %}
###### {{description[-1]}}
{% endfor %}

## Volunteering
{% for basic, description in zip(volunteering.basic, volunteering.description) %}
### {{basic[0]}}
> {{basic[1]}} — {{basic[2]}}

{{description[0]}}
###### {{basic[3]}}
{% endfor %}

## Certifications
{% for basic, description in zip(certifications.basic, certifications.description) %}
### {{basic[0]}}
> **{{basic[1]}}** — *{{basic[2]}}*

{{description[0]}}
{% endfor %}

## Projects
{% for basic, description, skills in zip(projects.basic, projects.description, projects.skills) %}
### {{basic[0]}}
{% if basic[1] %}
> {{basic[1]}}
{% endif %}
{{description[0]}}
###### {{skills[0]}}
{%endfor%}

## Languages
{% for language in languages.languages %}
- **{{language[0]}}**
  - {{language[1]}}
{% endfor %}
