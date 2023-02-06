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
    'kind',
    'alias_id/036c3d4167e26715b4b833dfac3087ea',
    'ref_1',
    'billing-docs',
    NULL,
    '{}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp
),
(
    20004,
    0,
    'kind',
    'alias_id/3f150c28acfb269d8e68e8b0a72e233b',
    'ref_1',
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
    'kind',
    'alias_id/4a20a5eafdfc36d4bc3fc25223e92382/commission/process',
    'ref_1',
    'billing-docs',
    NULL,
    '{}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp
),
(
    40004,
    0,
    'kind',
    'alias_id/63d700929bf33845b47840fd23ee0fce',
    'ref_1',
    'billing-docs',
    NULL,
    '{}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp
),
(
    50004,
    0,
    'kind',
    'alias_id/737336a3e8973c87942c9a6f7b1b7c39',
    'ref_1',
    'billing-docs',
    NULL,
    '{}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp
),
(
    60004,
    0,
    'kind',
    'alias_id/95757a8c4d892ca0838d2b00ce2cde38',
    'ref_1',
    'billing-docs',
    NULL,
    '{}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp
),
(
    70004,
    0,
    'kind',
    'alias_id/bd48f8e0e2ce2d1885b85c69fe5a48c0/commission',
    'ref_1',
    'billing-docs',
    NULL,
    '{}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp
),
(
    80004,
    0,
    'kind',
    'alias_id/d495a4d9ac17329ca3320edb2e53c2da',
    'ref_1',
    'billing-docs',
    NULL,
    '{}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp
),
(
    90004,
    0,
    'kind',
    'alias_id/e6a2529123c6554a862ed638cc75f916',
    'ref_1',
    'billing-docs',
    NULL,
    '{}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp
);
ALTER SEQUENCE bd_testsuite_04.doc_id_seq RESTART WITH 10;

INSERT INTO bd_testsuite_05.doc
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
    120005,
    0,
    'kind',
    'alias_id/0fb1f728097b2965be341e5db5b9f59c',
    'ref_1',
    'billing-docs',
    NULL,
    '{}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp
),
(
    130005,
    0,
    'kind',
    'alias_id/2cadabf6057e264ea95e3b45b8478cd4',
    'ref_1',
    'billing-docs',
    NULL,
    '{}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp
)
;

ALTER SEQUENCE bd_testsuite_05.doc_id_seq RESTART WITH 10;
