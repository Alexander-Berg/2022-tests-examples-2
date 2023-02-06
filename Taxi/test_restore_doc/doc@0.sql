ALTER SEQUENCE bd_testsuite_00.doc_id_seq RESTART WITH 22;

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
