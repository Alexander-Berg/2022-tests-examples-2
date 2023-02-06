INSERT INTO ba_testsuite_00.journal_replication_chunks
(
    last_journal_id,
    count,
    created,
    updated
)
VALUES
(
    20000,
    2,
    '2020-01-10 08:00:00.000000'::timestamp,
    '2020-01-10 08:00:00.000000'::timestamp
);

INSERT INTO ba_testsuite_02.journal_replication_chunks
(
    last_journal_id,
    count,
    created,
    updated
)
VALUES
(
    10002,
    2,
    '2020-01-10 08:00:00.000000'::timestamp,
    '2020-01-10 08:00:00.000000'::timestamp
);
