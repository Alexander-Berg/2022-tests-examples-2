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
),
(
    20000,
    1,
    2,
    'status_changed',
    '{"status": "new", "tags": ["taxi/unique_driver_id/5c615efb3fd6947b66fc2e79"]}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp
);
ALTER SEQUENCE bd_testsuite_00.event_seq_id_seq RESTART WITH 3;


INSERT INTO bd_testsuite_01.event
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
    40001,
    1,
    1,
    'status_changed',
    '{"status": "new", "tags": ["taxi/unique_driver_id/5c6527563fd6940450db7483"]}'::jsonb,
    '2018-09-04 07:07:52.019582'::timestamp
),
(
    50001,
    1,
    2,
    'status_changed',
    '{"status": "new", "tags": ["taxi/unique_driver_id/5c6527563fd6940450db7483"]}'::jsonb,
    '2018-09-05 07:07:52.019582'::timestamp
),
(
    60001,
    1,
    3,
    'status_changed',
    '{"status": "new", "tags": ["taxi/unique_driver_id/5c6527563fd6940450db7483"]}'::jsonb,
    '2018-09-06 07:07:52.019582'::timestamp
);
ALTER SEQUENCE bd_testsuite_01.event_seq_id_seq RESTART WITH 4;


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
),
(
    30002,
    1,
    3,
    'status_changed',
    '{"status": "complete"}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp
),
(
    50002,
    1,
    5,
    'status_changed',
    '{"status": "complete", "tags": ["taxi/unique_driver_id/5c615efb3fd6947b66fc2e79"]}'::jsonb,
    '2018-09-09 07:07:52.019582'::timestamp
),
(
    60002,
    1,
    6,
    'status_changed',
    '{"status": "complete", "tags": ["taxi/unique_driver_id/5c615efb3fd6947b66fc2e79"]}'::jsonb,
    '2018-09-11 07:07:52.019582'::timestamp
),
(
    70002,
    1,
    7,
    'status_changed',
    '{"status": "complete", "tags": ["taxi/unique_driver_id/5c615efb3fd6947b66fc2e79"]}'::jsonb,
    '2018-09-13 07:07:52.019582'::timestamp
);
ALTER SEQUENCE bd_testsuite_02.event_seq_id_seq RESTART WITH 8;
