CREATE TABLE foo(
    bar TIMESTAMP,
    col INT
);

CREATE INDEX foo ON foo(col);

SELECT *
FROM foo
ORDER BY 1;
