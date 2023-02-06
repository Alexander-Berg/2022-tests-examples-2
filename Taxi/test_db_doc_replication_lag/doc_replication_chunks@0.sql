INSERT INTO bd_testsuite_00.doc_replication_chunks
(
    last_event_seq_id,
    count,
    created,
    updated
)
VALUES
(
    10000,
    10000,
    '2020-01-10T08:00:00',
    '2020-01-10T08:00:00'
);

INSERT INTO bd_testsuite_02.doc_replication_chunks
(
    last_event_seq_id,
    count,
    created,
    updated
)
VALUES
(
    10002,
    1000,
    '2020-01-10T08:00:00',
    '2020-01-10T08:00:00'
);
