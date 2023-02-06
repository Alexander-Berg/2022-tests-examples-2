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
	30004,
	2,
    4,
    'status_changed',
    '{"status": "complete"}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp
),
(
	40004,
	1,
    5,
    'status_changed',
    '{"status": "new"}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp
),
(
	50004,
	1,
    6,
    'status_changed',
    '{"status": "new"}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp
),
(
    60004,
    1,
    7,
    'status_changed',
    '{"status": "complete", "tags": ["taxi/unique_driver_id/5c615efb3fd6947b66fc2e79"]}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp
),
(
    70004,
    1,
    8,
    'status_changed',
    '{"status": "complete", "tags": ["taxi/unique_driver_id/5c615efb3fd6947b66fc2e79"]}'::jsonb,
    '2018-09-12 07:07:52.019582'::timestamp
),
(
    80004,
    1,
    9,
    'status_changed',
    '{"status": "complete", "tags": ["taxi/unique_driver_id/5c615efb3fd6947b66fc2e79"]}'::jsonb,
    '2018-09-14 07:07:52.019582'::timestamp
);
ALTER SEQUENCE bd_testsuite_04.event_seq_id_seq RESTART WITH 10;
