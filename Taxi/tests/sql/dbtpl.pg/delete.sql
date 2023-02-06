DELETE
FROM
    "tst"
WHERE
    "name" IN ({{ lst | vlist }})

