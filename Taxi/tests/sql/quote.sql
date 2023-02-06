SELECT
    "id"
FROM
    "{{ tablename |i }}"
WHERE
        "id" = {{ val |q }}
    AND "name" = {{ name }}
