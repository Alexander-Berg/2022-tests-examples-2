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
    '{"status": "new", "tags": ["test_update_tag_index"]}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    'basic idempotency key',
    'new'
),
(
    20002,
    1,
    2,
    'status_changed',
    '{"status": "new"}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    'basic idempotency key',
    'new'
),
(
    30002,
    1,
    3,
    'status_changed',
    '{"status": "complete"}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    'basic idempotency key',
    'complete'
)
;
ALTER SEQUENCE bd_testsuite_02.event_seq_id_seq RESTART WITH 5;
