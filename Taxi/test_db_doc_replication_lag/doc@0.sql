INSERT INTO bd_testsuite_00.doc
(
    id,
    prev_doc_id,
    kind,
    external_obj_id,
    external_event_ref,
    service,
    service_user_id,
    data,
    process_at,
    event_at,
    created
)
VALUES
(
    10000,
    0,
    'test',
    'abc',
    'ride_order_completed',
    'billing-docs',
    NULL,
    '{"shoop": "da whoop"}'::jsonb,
    '2020-01-10T07:59:50',
    '2020-01-10T07:59:50',
    '2020-01-10T07:59:50'
),
(
    20000,
    10000,
    'test',
    'abc',
    'ride_order_amended',
    'billing-docs',
    NULL,
    '{"shoop": "da whoop"}'::jsonb,
    '2020-01-10T08:00:00',
    '2020-01-10T08:00:00',
    '2020-01-10T08:00:00'
);
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
	10000,
    'status_changed',
    '{"status": "new"}'::jsonb,
    '2020-01-10T07:59:50'
),
(
    20000,
    1,
    20000,
    'status_changed',
    '{"status": "new"}'::jsonb,
    '2020-01-10T08:00:00'
);

INSERT INTO bd_testsuite_01.doc
(
    id,
    prev_doc_id,
    kind,
    external_obj_id,
    external_event_ref,
    service,
    service_user_id,
    data,
    process_at,
    event_at,
    created
)
VALUES
(
    10001,
    0,
    'test',
    'abc',
    'ride_order_completed',
    'billing-docs',
    NULL,
    '{"shoop": "da whoop"}'::jsonb,
    '2020-01-10T07:58:20',
    '2020-01-10T07:58:20',
    '2020-01-10T07:58:20'
),
(
    20001,
    10001,
    'test',
    'abc',
    'ride_order_amended',
    'billing-docs',
    NULL,
    '{"shoop": "da whoop"}'::jsonb,
    '2020-01-10T07:59:50',
    '2020-01-10T07:59:50',
    '2020-01-10T07:59:00'
);
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
	10001,
	1,
	10001,
    'status_changed',
    '{"status": "new"}'::jsonb,
    '2020-01-10T07:58:20'
),
(
    20001,
    1,
    20001,
    'status_changed',
    '{"status": "new"}'::jsonb,
    '2020-01-10T07:59:00'
);
