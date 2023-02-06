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
    'kind',
    'cashback/10504340098',
    'ref_1',
    'billing-docs',
    NULL,
    '{"shoop": "da whoop"}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp
),
(
    20000,
    0,
    'kind',
    'cashback/6821580089',
    'ref_2',
    'billing-docs',
    NULL,
    '{}'::jsonb,
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
    'kind',
    'taxi/taximeter/payment/0c4f525fd41e29ae0dfd9cf90ddfd659',
    'ref_1',
    'billing-docs',
    NULL,
    '{}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp
),
(
    20002,
    0,
    'kind',
    'taxi/b2b_partner_payment/2a90feaca2226590b1a9612bf7e51981',
    'ref_2',
    'billing-docs',
    NULL,
    '{}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp
),
(
    30002,
    0,
    'kind',
    'taxi/taximeter/payment/dd685b52c64ef5501ccb97dd32591660',
    'ref_1',
    'billing-docs',
    NULL,
    '{}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp
),
(
    40002,
    0,
    'kind',
    'subvention_reasons_updates/alias_id/ec73dd1ecd7c2ae0862e174006517dd5',
    'ref_1',
    'billing-docs',
    NULL,
    '{}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp
);
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
    50003,
    0,
    'kind',
    'alias_id/a2ae8ca7b7d334628466548598b60081',
    'ref_1',
    'billing-docs',
    NULL,
    '{}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp
),
(
    60003,
    0,
    'kind',
    'cashback/8696860085',
    'ref_1',
    'billing-docs',
    NULL,
    '{}'::jsonb,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp,
    '2018-09-10 07:07:52.019582'::timestamp
),
(
    70003,
    0,
    'kind',
    'taxi/taximeter/payment/e2c23052f7a8a785188df904f8f22c1b',
    'ref_1',
    'billing-docs',
    NULL,
    '{}'::jsonb,
    '2018-09-11 07:07:52.019582'::timestamp,
    '2018-09-11 07:07:52.019582'::timestamp,
    '2018-09-11 07:07:52.019582'::timestamp
),
(
    80003,
    0,
    'kind',
    'cashback/7329800199/process',
    'ref_1',
    'billing-docs',
    NULL,
    '{}'::jsonb,
    '2018-09-11 07:07:52.019582'::timestamp,
    '2018-09-11 07:07:52.019582'::timestamp,
    '2018-09-11 07:07:52.019582'::timestamp
),
(
    90003,
    80003,
    'kind',
    'alias_id/37993f6e1cf321adb2cb2bfff3d95521/commission',
    'ref_1',
    'billing-docs',
    NULL,
    '{}'::jsonb,
    '2018-09-11 07:07:52.019582'::timestamp,
    '2018-09-11 07:07:52.019582'::timestamp,
    '2018-09-11 07:07:52.019582'::timestamp
),
(
    100003,
    0,
    'kind',
    'taxi/journal/bypass_b2b_trip_payment/b307e877c63916b599dea8b33cdc8f3a',
    'ref_1',
    'billing-docs',
    NULL,
    '{}'::jsonb,
    '2018-09-11 07:07:52.019582'::timestamp,
    '2018-09-11 07:07:52.019582'::timestamp,
    '2018-09-11 07:07:52.019582'::timestamp
);
ALTER SEQUENCE bd_testsuite_03.doc_id_seq RESTART WITH 7;
