INSERT INTO bd_testsuite_00.event
(
    doc_id,
    version,
    seq_id,
    kind,
    data,
    created
)
VALUES
(
    10000,
    1,
    1,
    'status_changed',
    '{"status": "new"}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp
);
ALTER SEQUENCE bd_testsuite_00.event_seq_id_seq RESTART WITH 2;

INSERT INTO bd_testsuite_02.event
(
    doc_id,
    version,
    seq_id,
    kind,
    data,
    created
)
VALUES
(
    10002,
    1,
    1,
    'status_changed',
    '{"status": "new"}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp
),
(
    20002,
    1,
    2,
    'status_changed',
    '{"status": "new"}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp
);
ALTER SEQUENCE bd_testsuite_02.event_seq_id_seq RESTART WITH 3;
