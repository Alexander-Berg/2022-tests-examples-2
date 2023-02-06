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
    10,
    'status_changed',
    '{"status": "new"}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    'basic idempotency key',
    'new'
),
(
	20004,
	1,
    20,
    'status_changed',
    '{"status": "new"}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    'basic idempotency key',
    'new'
),
(
	30004,
	1,
    30,
    'status_changed',
    '{"status": "new"}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    'basic idempotency key',
    'new'
),
(
	30004,
	2,
    40,
    'status_changed',
    '{"status": "complete"}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    'basic idempotency key',
    'complete'
),
(
	40004,
	1,
    50,
    'status_changed',
    '{"status": "new"}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    null,
    null
),
(
	50004,
	1,
    60,
    'status_changed',
    '{"status": "new"}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    null,
    null
),
(
	60004,
	1,
    70,
    'status_changed',
    '{"status": "complete"}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    'basic idempotency key',
    'complete'
),
(
	70004,
	1,
    80,
    'status_changed',
    '{"status": "complete"}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    null,
    null
),
(
	80004,
	1,
    90,
    'status_changed',
    '{"status": "new"}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    null,
    null
),
(
	90004,
	1,
    100,
    'status_changed',
    '{"status": "complete"}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    'basic idempotency key',
    'complete'
);
ALTER SEQUENCE bd_testsuite_04.event_seq_id_seq RESTART WITH 110;
