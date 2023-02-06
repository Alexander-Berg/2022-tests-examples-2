INSERT INTO bd_testsuite_00.event
(
    doc_id,
    version,
    seq_id,
    kind,
    data,
    created,
    idempotency_key,
    status
)
VALUES
(
	10000,
	1,
    1,
    'status_changed',
    '{"status": "new"}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    null,
    null
),
(
    20000,
    1,
    2,
    'status_changed',
    '{"status": "new"}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    null,
    null
);
ALTER SEQUENCE bd_testsuite_00.event_seq_id_seq RESTART WITH 3;


INSERT INTO bd_testsuite_02.event
(
    doc_id,
    version,
    seq_id,
    kind,
    data,
    created,
    idempotency_key,
    status
)
VALUES
(
	10002,
	1,
    1,
    'status_changed',
    '{"status": "new"}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    'ikey',
    'new'
),
(
    20002,
    1,
    2,
    'status_changed',
    '{"status": "new"}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    'ikey',
    'new'
),
(
    30002,
    1,
    3,
    'status_changed',
    '{"status": "complete"}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    'ikey',
    'complete'
),
(
    40002,
    1,
    4,
    'status_changed',
    '{"status": "complete"}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    'ikey',
    'complete'
);
ALTER SEQUENCE bd_testsuite_02.event_seq_id_seq RESTART WITH 5;

INSERT INTO bd_testsuite_03.event
(
    doc_id,
    version,
    seq_id,
    kind,
    data,
    created,
    idempotency_key,
    status
)
VALUES
(
	50003,
	1,
    1,
    'status_changed',
    '{"status": "complete"}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    null,
    null
),
(
    60003,
    1,
    2,
    'status_changed',
    '{"status": "complete"}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    null,
    null
),
(
    70003,
    1,
    3,
    'status_changed',
    '{"status": "complete"}'::jsonb,
    '2018-09-11 07:07:52.019582'::timestamp,
    null,
    null
),
(
    80003,
    1,
    4,
    'status_changed',
    '{"status": "complete"}'::jsonb,
    '2018-09-11 07:07:52.019582'::timestamp,
    null,
    null
),
(
    90003,
    1,
    5,
    'status_changed',
    '{"status": "complete"}'::jsonb,
    '2018-09-11 07:07:52.019582'::timestamp,
    null,
    null
),
(
    100003,
    1,
    6,
    'status_changed',
    '{"status": "complete"}'::jsonb,
    '2018-09-11 07:07:52.019582'::timestamp,
    null,
    null
),
(
    100003,
    2,
    7,
    'status_changed',
    '{"status": "complete"}'::jsonb,
    '2018-09-11 07:07:52.019582'::timestamp,
    null,
    null
);
ALTER SEQUENCE bd_testsuite_03.event_seq_id_seq RESTART WITH 8;
