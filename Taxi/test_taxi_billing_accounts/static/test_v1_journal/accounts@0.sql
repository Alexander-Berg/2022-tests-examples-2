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
    '2018-08-15T22:00:00'
),
(
    41000,
    'unique_driver_id/583d4789250dd4071d3f6c09',
    'ag-rule-nMFG-000',
    'RUB',
    'income',
    '2018-08-09 17:00:54.048523',
    '2018-08-15T22:00:00'
),
(
    42000,
    'unique_driver_id/583d4789250dd4071d3f6c09',
    'ag-rule-nMFG-001',
    'XXX',
    'num_orders',
    '2018-08-09 17:00:54.048523',
    '2018-08-15T22:00:00'
),
(
    43000,
    'unique_driver_id/583d4789250dd4071d3f6c09',
    'ag-rule-nMFG-001',
    'RUB',
    'income',
    '2018-08-09 17:00:54.048523',
    '2018-08-15T22:00:00'
),
(
    45000,
    'unique_driver_id/583d4789250dd4071d3f6c09',
    'some_agreement',
    'XXX',
    'some_sub_account',
    '2018-08-09 17:00:54.048523',
    '2018-08-15T22:00:00'
),
(
    46000,
    'unique_driver_id/583d4789250dd4071d3f6c09',
    'some_agreement',
    'XXX',
    'su!_account',
    '2018-08-09 17:00:54.048523',
    '2018-08-15T22:00:00'
),
(
    47000,
    'unique_driver_id/583d4789250dd4071d3f6c09',
    'some_agreement',
    'XXX',
    'su!maccount',
    '2018-08-09 17:00:54.048523',
    '2018-08-15T22:00:00'
)
;
