INSERT INTO bd_testsuite_04.event
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
	10004,
	1,
    1,
    'status_changed',
    '{"status": "new"}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    'ikey',
    'new'
),
(
	20004,
	1,
    2,
    'status_changed',
    '{"status": "new"}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    'ikey',
    'new'
),
(
	30004,
	1,
    3,
    'status_changed',
    '{"status": "new"}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    'ikey',
    'new'
),
(
	30004,
	2,
    4,
    'status_changed',
    '{"status": "complete"}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    'ikey',
    'complete'
),
(
	40004,
	1,
    5,
    'status_changed',
    '{"status": "new"}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    null,
    null
),
(
	50004,
	1,
    6,
    'status_changed',
    '{"status": "new"}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    null,
    null
),
(
	60004,
	1,
    7,
    'status_changed',
    '{"status": "complete"}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    'ikey',
    'complete'
),
(
	70004,
	1,
    8,
    'status_changed',
    '{"status": "complete"}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    null,
    null
),
(
	80004,
	1,
    9,
    'status_changed',
    '{"status": "new"}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    null,
    null
),
(
	90004,
	1,
    10,
    'status_changed',
    '{"status": "complete"}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    'ikey',
    'complete'
);
ALTER SEQUENCE bd_testsuite_04.event_seq_id_seq RESTART WITH 11;

INSERT INTO bd_testsuite_05.event
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
	120005,
	1,
    1,
    'status_changed',
    '{"status": "new"}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    'ikey',
    'new'
),
(
	130005,
	1,
    2,
    'status_changed',
    '{"status": "new"}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    'ikey',
    'new'
);

ALTER SEQUENCE bd_testsuite_05.event_seq_id_seq RESTART WITH 10;
