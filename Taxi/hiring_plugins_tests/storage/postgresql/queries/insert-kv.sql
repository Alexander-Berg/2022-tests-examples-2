INSERT INTO
    "hiring_plugins_tests"."test"
    (
        "key",
        "value"
    )
VALUES
    ($1::TEXT, $2::TEXT)
RETURNING
    *
