INSERT INTO ba_testsuite_00.entity(external_id, kind, created)
VALUES
(
    'unique_driver_id/583d4789250dd4071d3f6c09',
    'driver',
    '2020-01-10T08:00:00'
);

INSERT INTO ba_testsuite_01.entity(external_id, kind, created)
VALUES
(
    'unique_driver_id/5b0913df30a2e52b7633b3e6',
    'driver',
    '2020-01-10T08:00:00'
);


INSERT INTO ba_testsuite_00.account
(
    id,
    entity_external_id,
    agreement_id,
    currency,
    sub_account,
    opened,
    expired
)
VALUES
(
    40000,
    'unique_driver_id/583d4789250dd4071d3f6c09',
    'ag-rule-nMFG-000',
    'XXX',
    'num_orders',
    '2018-08-09 17:00:54.048523',
    '2019-08-15T22:00:00'
);

INSERT INTO ba_testsuite_01.account
(
    id,
    entity_external_id,
    agreement_id,
    currency,
    sub_account,
    opened,
    expired
)
VALUES
(
    10001,
    'unique_driver_id/5b0913df30a2e52b7633b3e6',
    'ag-rule-nMFG-000',
    'XXX',
    'num_orders',
    '2018-08-09 17:00:54.048523',
    '2019-08-15T22:00:00'
);


INSERT INTO ba_testsuite_00.journal(id, account_id, amount, doc_ref, event_at, created, details)
VALUES
(
    10000,
    40000,
    '1',
    '1010000',
    '2020-01-10T07:00:00',
    '2020-01-10T07:00:00',
    NULL
),
(
    20000,
    40000,
    '1',
    '1020000',
    '2020-01-10T07:59:50',
    '2020-01-10T07:59:50',
    NULL
);

INSERT INTO ba_testsuite_01.journal(id, account_id, amount, doc_ref, event_at, created, details)
VALUES
(
    10001,
    10001,
    '1',
    '1110000',
    '2020-01-10T07:58:20',
    '2020-01-10T07:58:20',
    NULL
),
(
    20001,
    10001,
    '1',
    '1120000',
    '2020-01-10T07:59:50',
    '2020-01-10T07:59:00',
    NULL
);
