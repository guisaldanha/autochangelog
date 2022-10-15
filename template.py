template = """# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

{% for tag in changelog %}

## {% if remote_git %}[{{ tag['tag'] }}]({{remote_git}}/releases/tag/{{tag['tag']}}){% else %}{{tag['tag']}}{% endif %} - {% if tag['message']|length > 1 %}{{ tag['message'] }} - {% endif %}{{ tag['date'] }}

{% for changes in tag['changes'] %}

{% if changes != '' %}

### {{ changes }}

{% endif %}

{% for commit in tag['changes'][changes] %}

- {{ commit['message'] }}{% if commit['user'] %} - [@{{commit['user']}}](https://github.com/{{commit['user']}}) {% endif %} - {{commit['date']}} {% if remote_git %}([{{commit['hash']}}]({{remote_git}}/commit/{{commit['hash']}})){% else %}({{commit['hash']}}){% endif %}

{% endfor %}
{% endfor %}
{% endfor %}"""
