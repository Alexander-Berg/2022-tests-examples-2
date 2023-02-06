INSERT INTO bd_testsuite_04.doc
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
    10004,
    0,
    'test',
    'queue_1',
    'unprocessed_doc',
    'billing-docs',
    NULL,
    '{}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp
),
(
    20004,
    10004,
    'test',
    'queue_1',
    'doc_waiting_for_previous_to_complete',
    'billing-docs',
    NULL,
    '{}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp
),
(
    30004,
    0,
    'test',
    'queue_2',
    'doc_scheduled_in_future',
    'billing-docs',
    NULL,
    '{}'::jsonb,
    '2018-10-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp
),
(
    40004,
    0,
    'test',
    'queue_5',
    'complete_doc',
    'billing-docs',
    NULL,
    '{}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp
);
ALTER SEQUENCE bd_testsuite_04.doc_id_seq RESTART WITH 5;

INSERT INTO bd_testsuite_07.doc
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
    10007,
    0,
    'test',
    'queue_6',
    'incomplete_doc',
    'billing-docs',
    NULL,
    '{}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp
)
;
ALTER SEQUENCE bd_testsuite_07.doc_id_seq RESTART WITH 3;
