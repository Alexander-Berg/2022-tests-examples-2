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
    'alias_id/10b3a1c7dff04f0cb17a2374ef1bfe4d',
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
    'subvention_journal',
    'alias_id/10b3a1c7dff04f0cb17a2374ef1bfe4d',
    'ride_order_amended',
    'billing-docs',
    NULL,
    '{}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp
);
ALTER SEQUENCE bd_testsuite_00.doc_id_seq RESTART WITH 3;


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
    40001,
    30001,
    'subvention_journal',
    'alias_id/b078333377f94f9b8c30e13c783906d7',
    'order_subvention_changed/4/subvention_handled',
    'billing-docs',
    NULL,
    '{}'::jsonb,
    '2018-09-04 07:07:52.019582'::timestamp,
    '2018-09-04 07:07:52.019582'::timestamp,
    '2018-09-04 07:07:52.019582'::timestamp
),
(
    50001,
    40001,
    'subvention_journal',
    'alias_id/b078333377f94f9b8c30e13c783906d7',
    'order_subvention_changed/5/subvention_handled',
    'billing-docs',
    NULL,
    '{}'::jsonb,
    '2018-09-05 07:07:52.019582'::timestamp,
    '2018-09-05 07:07:52.019582'::timestamp,
    '2018-09-05 07:07:52.019582'::timestamp
),
(
    60001,
    50001,
    'subvention_journal',
    'alias_id/b078333377f94f9b8c30e13c783906d7',
    'order_subvention_changed/6/subvention_handled',
    'billing-docs',
    NULL,
    '{}'::jsonb,
    '2018-09-06 07:07:52.019582'::timestamp,
    '2018-09-06 07:07:52.019582'::timestamp,
    '2018-09-06 07:07:52.019582'::timestamp
);
ALTER SEQUENCE bd_testsuite_01.doc_id_seq RESTART WITH 7;


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
),
(
    50002,
    0,
    'subvention_journal',
    'alias_id/ee2c3590533744cda11b5e5fc00ffebf',
    'order_subvention_changed/1/subvention_handled',
    'billing-docs',
    NULL,
    '{}'::jsonb,
    '2018-09-09 07:07:52.019582'::timestamp,
    '2018-09-09 07:07:52.019582'::timestamp,
    '2018-09-09 07:07:52.019582'::timestamp
),
(
    60002,
    50002,
    'subvention_journal',
    'alias_id/ee2c3590533744cda11b5e5fc00ffebf',
    'order_subvention_changed/2/subvention_handled',
    'billing-docs',
    NULL,
    '{}'::jsonb,
    '2018-09-11 07:07:52.019582'::timestamp,
    '2018-09-11 07:07:52.019582'::timestamp,
    '2018-09-11 07:07:52.019582'::timestamp
),
(
    70002,
    60002,
    'subvention_journal',
    'alias_id/ee2c3590533744cda11b5e5fc00ffebf',
    'order_subvention_changed/3/subvention_handled',
    'billing-docs',
    NULL,
    '{}'::jsonb,
    '2018-09-13 07:07:52.019582'::timestamp,
    '2018-09-13 07:07:52.019582'::timestamp,
    '2018-09-13 07:07:52.019582'::timestamp
);
ALTER SEQUENCE bd_testsuite_02.doc_id_seq RESTART WITH 8;
