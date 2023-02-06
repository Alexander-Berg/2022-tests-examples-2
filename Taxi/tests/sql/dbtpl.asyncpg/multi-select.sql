SELECT
    "column1" AS "a",
    "column2" AS "b"
FROM (VALUES 
    ({{ 'a' }}::TEXT, {{ 'b' }}::TEXT),
    ({{ a }}::TEXT, {{ b }}::TEXT)
) AS "t"
