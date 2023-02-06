SELECT
    *
FROM
    "tst"
WHERE
    "name" IN ({{ lst |vlist }})
ORDER BY
    "name"
