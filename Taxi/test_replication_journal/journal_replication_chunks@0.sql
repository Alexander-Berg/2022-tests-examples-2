INSERT INTO ba_testsuite_00.journal_replication_chunks
(
    last_journal_id,
    count,
    created,
    updated
)
VALUES
(
    22220020000,
    2,
    '2019-01-30 00:00:00.000000'::timestamp,
    '2019-01-30 00:00:00.000000'::timestamp
),
( -- this is partially rolled chunk
    22220050000,
    3,
    '2019-01-30 00:00:00.000000'::timestamp,
    '2019-01-30 00:00:00.000000'::timestamp
),
( -- incomplete chunk (overfilled)
    22220090000,
    3,
    '2019-01-30 00:00:00.000000'::timestamp,
    '2019-01-30 00:00:00.000000'::timestamp
);
