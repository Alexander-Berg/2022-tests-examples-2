WITH "a" AS (
    SELECT
        "column1" AS "a",
        "column2" AS "b"
    FROM (VALUES 
        ({{ 'a' }}::TEXT, {{ 'b' }}::TEXT)
    ) AS "t"
)
SELECT
    *
FROM
    "a"
WHERE
    FALSE = TRUE
