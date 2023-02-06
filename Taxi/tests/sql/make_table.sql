SELECT
    "column1" AS "{{ 'id' | i }}",
    "column2" AS "{{ 'value' | i }}"
FROM
(
    VALUES
    {% for i in range(count) %}
        ({{ i }}::INTEGER, {{ (i * 10) | string }}::TEXT){%- if loop.last %}{% else %},{% endif -%}
    {% endfor %}
) AS "t"
