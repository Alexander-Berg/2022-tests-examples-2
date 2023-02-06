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
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp
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
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp
);
ALTER SEQUENCE bd_testsuite_00.doc_id_seq RESTART WITH 3;


INSERT INTO bd_testsuite_02.doc
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
    10002,
    0,
    'test',
    'queue_3',
    'new->complete',
    'billing-docs',
    NULL,
    '{}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp
),
(
    20002,
    10002,
    'test',
    'queue_3',
    'new->complete with details',
    'billing-docs',
    NULL,
    '{}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp
),
(
    30002,
    20002,
    'test',
    'queue_3',
    'complete->complete',
    'billing-docs',
    NULL,
    '{}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp
)
;
ALTER SEQUENCE bd_testsuite_02.doc_id_seq RESTART WITH 5;

INSERT INTO bd_testsuite_03.doc
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
    50002,
    0,
    'test',
    'select_docs_test',
    '1',
    'billing-docs',
    NULL,
    '{}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp
),
(
    60002,
    50002,
    'test',
    'select_docs_test',
    '2',
    'billing-docs',
    NULL,
    '{}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp
),
(
    70002,
    60002,
    'test',
    'select_docs_test',
    '3',
    'billing-docs',
    NULL,
    '{}'::jsonb,
    '2018-09-11 07:07:52.019582'::timestamp,
    '2018-09-11 07:07:52.019582'::timestamp,
    '2018-09-11 07:07:52.019582'::timestamp
),
(
    80002,
    70002,
    'test',
    'select_docs_test',
    '4',
    'billing-docs',
    NULL,
    '{}'::jsonb,
    '2018-09-11 07:07:52.019582'::timestamp,
    '2018-09-11 07:07:52.019582'::timestamp,
    '2018-09-11 07:07:52.019582'::timestamp
),
(
    90002,
    80002,
    'test_details',
    'select_test_dets',
    '5',
    'billing-docs',
    NULL,
    '{}'::jsonb,
    '2018-09-11 07:07:52.019582'::timestamp,
    '2018-09-11 07:07:52.019582'::timestamp,
    '2018-09-11 07:07:52.019582'::timestamp
),
(
    100002,
    90002,
    'test_details',
    'select_test_dets',
    '6',
    'billing-docs',
    NULL,
    '{"doc_field": {"some_key": "some_data"}}'::jsonb,
    '2018-09-11 07:07:52.019582'::timestamp,
    '2018-09-11 07:07:52.019582'::timestamp,
    '2018-09-11 07:07:52.019582'::timestamp
);
ALTER SEQUENCE bd_testsuite_03.doc_id_seq RESTART WITH 7;
