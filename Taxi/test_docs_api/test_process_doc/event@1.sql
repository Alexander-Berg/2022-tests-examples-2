INSERT INTO bd_testsuite_04.event
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
	10004,
	1,
    1,
    'status_changed',
    '{"status": "new"}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp
),
(
    20004,
    1,
    2,
    'status_changed',
    '{"status": "new"}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp
),
(
    30004,
    1,
    3,
    'status_changed',
    '{"status": "new"}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp
),
(
    40004,
    1,
    4,
    'status_changed',
    '{"status": "new"}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp
);
ALTER SEQUENCE bd_testsuite_04.event_seq_id_seq RESTART WITH 5;

INSERT INTO bd_testsuite_07.event
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
	10007,
	1,
    1,
    'status_changed',
    '{"status": "new"}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp
)
;
ALTER SEQUENCE bd_testsuite_07.event_seq_id_seq RESTART WITH 3;
