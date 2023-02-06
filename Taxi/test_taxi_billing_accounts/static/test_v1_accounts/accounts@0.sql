INSERT INTO ba_testsuite_01.account
(
    id,
    entity_external_id,
    agreement_id,
    currency,
    sub_account,
    opened,
    expired,
    updates,
    updated
)
VALUES
(
    50001,
    'unique_driver_id/5b0913df30a2e52b7633b3e6',
    'ag-testsuite-nMFG-000',
    'RUB',
    'income',
    '2018-08-09T17:05:41.406741',
    '2018-08-15T22:00:00',
    NULL,
    '2018-08-09T17:05:41.406741'
),
(
    51001,
    'unique_driver_id/5b0913df30a2e52b7633b3e6',
    'ag-testsuite-nMFG-000',
    'XXX',
    'num_orders',
    '2018-08-09T17:05:41.651405',
    '2109-07-18T17:26:31.000000',
    '[{"data": {"expired": 253402300799999999}, "created": 1533834341651410}, {"data": {"expired": 4403611591000000}, "created": 1637749366324790, "doc_ref": "doc_ref", "idempotency_key": "idempotency_key"}]'::jsonb,
    '2021-11-24T10:22:46.324790'
),
(
    9740001,
    'unique_driver_id/5b0913df30a2e52b7633b3e6',
    'subvention_agreement/voronezh_daily_guarantee_2018',
    'RUB',
    'income',
    '2018-11-23T09:12:37.281163',
    'infinity',
    NULL,
    '2018-11-23T09:12:37.281163'
),
(
    20001,
    'unique_driver_id/5ac2856ae342c7944bff60b6',
    'subvention_agreement/2018_10_17',
    'XXX',
    'num_orders',
    '2018-07-09T16:31:52.758819',
    '2018-09-10T22:00:00',
    NULL,
    '2018-07-09T16:31:52.758819'
),
(
    5256730001,
    'unique_driver_id/5ac2856ae342c7944bff60b6',
    'subvention_agreement/2018_10_17',
    'RUB',
    'net',
    '2018-07-09T16:31:52.758819',
    '2018-09-10T22:00:00',
    NULL,
    '2018-07-09T16:31:52.758819'
);