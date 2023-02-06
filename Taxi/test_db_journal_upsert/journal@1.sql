INSERT INTO ba_testsuite_04.entity(external_id, kind, created)
VALUES
(
    'unique_driver_id/5b6b177a41e102a72fa4e223',
    'driver',
    '2018-09-02T00:00:00'
);

INSERT INTO ba_testsuite_05.entity(external_id, kind, created)
VALUES
(
    'unique_driver_id/598c4d2689216ea4eee49939',
    'driver',
    '2018-09-02T00:00:00'
);


INSERT INTO ba_testsuite_04.account
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
    40004,
    'unique_driver_id/5b6b177a41e102a72fa4e223',
    'ag-subv-001',
    'RUB',
    'income',
    '2018-10-09 16:33:28.895876',
    '2018-12-15 22:00:00'
),
(
    140004,
    'unique_driver_id/5b6b177a41e102a72fa4e223',
    'ag-subv-001',
    'XXX',
    'num_orders',
    '2018-10-09 16:33:28.895876',
    '2018-12-15 22:00:00'
);

INSERT INTO ba_testsuite_05.account
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
    10005,
    'unique_driver_id/598c4d2689216ea4eee49939',
    'ag-subv-001',
    'RUB',
    'income',
    '2018-10-09 16:33:28.895876',
    '2018-12-15 22:00:00'
)
