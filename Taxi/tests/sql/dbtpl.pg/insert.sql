INSERT INTO "tst" ("name")

VALUES

{% for n in lst %}
    ({{ n }}){% if not loop.last %},{% endif %}
{% endfor %}


