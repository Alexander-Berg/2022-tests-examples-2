INSERT INTO ba_testsuite_03.entity(external_id, kind, created)
VALUES
(
    'unique_driver_id/5adf9c23a3ddb1256a8542b8',
    'driver',
    '2018-06-01T00:00:00'
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
    31370003,
    'unique_driver_id/5adf9c23a3ddb1256a8542b8',
    'ag-rule-nMFG-000',
    'RUB',
    'income',
    '2018-08-09 17:00:54.048523',
    '2019-01-01 00:00:00'
);

INSERT INTO ba_testsuite_03.balance_at
(
    account_id,
    accrued_at,
    balance,
    journal_id
)
VALUES
(
    31370003,
    '2018-10-03 23:00:00.000000',
    1000.0,
    10003
);
