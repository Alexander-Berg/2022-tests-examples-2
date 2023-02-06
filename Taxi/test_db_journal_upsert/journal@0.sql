INSERT INTO ba_testsuite_00.entity(external_id, kind, created)
VALUES
(
    'unique_driver_id/583d4789250dd4071d3f6c09',
    'driver',
    '2018-01-03T00:00:00'
);

INSERT INTO ba_testsuite_01.entity(external_id, kind, created)
VALUES
(
    'unique_driver_id/5b0913df30a2e52b7633b3e6',
    'driver',
    '2018-01-03T01:00:00'
);

INSERT INTO ba_testsuite_02.entity(external_id, kind, created)
VALUES
(
    'unique_driver_id/5b6c154741e102a72fddf926',
    'driver',
    '2018-01-03T02:00:00'
);

INSERT INTO ba_testsuite_03.entity(external_id, kind, created)
VALUES
(
    'unique_driver_id/5adf9c23a3ddb1256a8542b8',
    'driver',
    '2018-01-03T02:00:00'
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
),
(
    50000,
    'unique_driver_id/583d4789250dd4071d3f6c09',
    'ag-rule-nMFG-000',
    'RUB',
    'income',
    '2018-08-09 17:00:54.048523',
    '2019-08-15T22:00:00'
)
;

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
),
(
    20001,
    'unique_driver_id/5b0913df30a2e52b7633b3e6',
    'ag-rule-nMFG-000',
    'RUB',
    'income',
    '2018-08-09 17:00:54.048523',
    '2019-09-19 22:00:00'
);

INSERT INTO ba_testsuite_02.account
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
    10002,
    'unique_driver_id/5b6c154741e102a72fddf926',
    'ag-rule-nMFG-000',
    'USD',
    'commission',
    '2018-09-09 17:00:54.048523',
    '2019-09-15T22:00:00'
);

INSERT INTO ba_testsuite_03.account
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
    10003,
    'unique_driver_id/5adf9c23a3ddb1256a8542b8',
    'ag-rule-nMFG-001',
    'XXX',
    'num_orders',
    '2018-08-09 17:00:54.048523',
    '2019-08-15T22:00:00'
),
(
    20003,
    'unique_driver_id/5adf9c23a3ddb1256a8542b8',
    'ag-rule-nMFG-001',
    'RUB',
    'income',
    '2018-08-09 17:00:54.048523',
    '2019-09-19 22:00:00'
),
(
    30003,
    'unique_driver_id/5adf9c23a3ddb1256a8542b8',
    'ag-rule-nMFG-001',
    'RUB',
    'commission',
    '2018-08-09 17:00:54.048523',
    '2019-09-19 22:00:00'
);
