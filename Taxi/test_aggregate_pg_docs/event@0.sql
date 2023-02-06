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
    10,
    'status_changed',
    '{"status": "new"}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    null,
    null
),
(
    20000,
    1,
    20,
    'status_changed',
    '{"status": "new", "tags": ["deadfood"]}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    null,
    null
);
ALTER SEQUENCE bd_testsuite_00.event_seq_id_seq RESTART WITH 30;


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
    10,
    'status_changed',
    '{"status": "new", "tags": ["test_update_tag_index"]}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    'basic idempotency key',
    'new'
),
(
    20002,
    1,
    20,
    'status_changed',
    '{"status": "new"}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    'basic idempotency key',
    'new'
),
(
    30002,
    1,
    30,
    'status_changed',
    '{"status": "complete"}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    'basic idempotency key',
    'complete'
)
;
ALTER SEQUENCE bd_testsuite_02.event_seq_id_seq RESTART WITH 50;

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
	50002,
	1,
    10,
    'status_changed',
    '{"status": "complete"}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    null,
    null
),
(
    60002,
    1,
    20,
    'status_changed',
    '{"status": "complete"}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    null,
    null
),
(
    70002,
    1,
    30,
    'status_changed',
    '{"status": "complete"}'::jsonb,
    '2018-09-11 07:07:52.019582'::timestamp,
    null,
    null
),
(
    80002,
    1,
    40,
    'status_changed',
    '{"status": "complete"}'::jsonb,
    '2018-09-11 07:07:52.019582'::timestamp,
    null,
    null
),
(
    90002,
    1,
    50,
    'status_changed',
    '{"status": "complete", "details": {"reason": "Skipped by version"}}'::jsonb,
    '2018-09-11 07:07:52.019582'::timestamp,
    null,
    null
),
(
    100002,
    1,
    60,
    'status_changed',
    '{"status": "complete", "details": {"reason": "reason_1", "field_1": "info_1"}}'::jsonb,
    '2018-09-11 07:07:52.019582'::timestamp,
    null,
    null
),
(
    100002,
    2,
    70,
    'status_changed',
    '{"status": "complete", "details": {"reason": "reason_2", "field_2": "info_2"}}'::jsonb,
    '2018-09-11 07:07:52.019582'::timestamp,
    null,
    null
);
ALTER SEQUENCE bd_testsuite_03.event_seq_id_seq RESTART WITH 80;
